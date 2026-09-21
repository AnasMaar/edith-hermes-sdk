"""Production semantics behind the generated SDK operation catalog."""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

from edith_hermes.generated.operations import HERMES_RPC_METHODS

from .auth import Identity
from .config import Settings
from .database import Database, DurableJob
from .gateway import HermesGateway
from .providers import RuntimeRegistry


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Problem(Exception):
    def __init__(self, status: int, title: str, detail: str, *, retryable: bool = False):
        self.status = status
        self.payload = {
            "type": "about:blank",
            "title": title,
            "status": status,
            "detail": detail,
            "retryable": retryable,
        }
        super().__init__(detail)


class ProductionEngine:
    def __init__(
        self,
        database: Database,
        settings: Settings,
        runtimes: RuntimeRegistry,
        gateway: HermesGateway,
    ):
        self.database = database
        self.settings = settings
        self.runtimes = runtimes
        self.gateway = gateway

    @staticmethod
    def _id(prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex}"

    @staticmethod
    def _digest(value: Any) -> str:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        return "sha256:" + hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _verify_owner(body: dict[str, Any], identity: Identity) -> None:
        requested = body.get("owner")
        if requested and (
            requested.get("tenantId") != identity.tenant_id
            or requested.get("subjectId") != identity.subject_id
        ):
            raise Problem(403, "Forbidden", "Resource ownership must match the bearer identity")

    async def required(self, kind: str, resource_id: str, identity: Identity) -> dict[str, Any]:
        value = await self.database.get(kind, resource_id, identity.owner)
        if value is None:
            raise Problem(404, "Not found", f"{kind} {resource_id} was not found")
        return value

    async def _instance(self, instance_id: str, identity: Identity) -> dict[str, Any]:
        return await self.required("instance", instance_id, identity)

    async def _native(
        self, instance_id: str, identity: Identity, method: str, params: Any = None
    ) -> dict[str, Any]:
        instance = await self._instance(instance_id, identity)
        if instance.get("status") != "ready":
            raise Problem(409, "Instance unavailable", "The Hermes instance is not ready")
        return await self.gateway.invoke(instance["connection"], method, params)

    @staticmethod
    def _build_document(job: DurableJob) -> dict[str, Any]:
        statuses = {
            "queued": "queued",
            "running": "building",
            "succeeded": "succeeded",
            "failed": "failed",
            "cancelled": "cancelled",
        }
        value = {
            "id": job.job_id,
            "owner": {"tenantId": job.tenant_id, "subjectId": job.subject_id},
            "status": statuses[job.status],
            "progress": 100 if job.status == "succeeded" else 20 if job.status == "running" else 0,
            "error": job.error,
            "createdAt": job.created_at.isoformat(),
            "completedAt": job.completed_at.isoformat() if job.completed_at else None,
        }
        if job.result:
            value["imageId"] = job.result.get("imageId")
        return value

    @staticmethod
    def _provision_document(job: DurableJob) -> dict[str, Any]:
        phases = {
            "queued": "queued",
            "running": "creating_instance",
            "succeeded": "ready",
            "failed": "failed",
            "cancelled": "cancelled",
        }
        value = {
            "id": job.job_id,
            "owner": {"tenantId": job.tenant_id, "subjectId": job.subject_id},
            "phase": phases[job.status],
            "error": job.error,
            "createdAt": job.created_at.isoformat(),
            "completedAt": job.completed_at.isoformat() if job.completed_at else None,
        }
        if job.result:
            value.update(job.result)
        return value

    async def handle(
        self, operation_id: str, arguments: dict[str, Any], identity: Identity
    ) -> tuple[int, Any]:
        body = arguments.get("body") or {}
        if isinstance(body, dict):
            self._verify_owner(body, identity)

        if operation_id == "getControlPlaneCapabilities":
            url = self.settings.database_url
            state = (
                "memory"
                if ":memory:" in url
                else "sqlite"
                if url.startswith("sqlite")
                else "postgresql"
                if url.startswith("postgresql")
                else "sql"
            )
            return 200, {
                "runtimeProviders": self.runtimes.kinds,
                "stateBackend": state,
                "authentication": self.settings.auth_mode,
                "imageSecurity": {
                    "digestPinnedBase": self.settings.require_digest_pinned_base,
                    "vulnerabilityScan": self.settings.require_image_scan,
                    "signature": self.settings.require_image_signature,
                },
                "durableJobs": True,
                "multiReplicaSafe": state == "postgresql",
            }

        if operation_id == "createImageRecipe":
            recipe_id = self._id("recipe")
            recipe = {
                **body,
                "id": recipe_id,
                "recipeDigest": self._digest(body),
                "createdAt": now(),
            }
            await self.database.put("recipe", recipe_id, identity.owner, recipe)
            return 201, recipe
        if operation_id == "listImageRecipes":
            return 200, {
                "items": await self.database.list("recipe", identity.owner),
                "nextCursor": None,
            }
        if operation_id == "getImageRecipe":
            return 200, await self.required("recipe", arguments["recipeId"], identity)
        if operation_id == "deleteImageRecipe":
            await self.required("recipe", arguments["recipeId"], identity)
            await self.database.delete("recipe", arguments["recipeId"], identity.owner)
            return 204, None
        if operation_id == "startImageBuild":
            job_id = self._id("build")
            await self.database.enqueue(job_id, "image_build", identity.owner, body)
            job = await self.database.get_job(job_id, identity.owner)
            assert job is not None
            return 202, self._build_document(job)
        if operation_id == "listImageBuilds":
            jobs = await self.database.list_jobs("image_build", identity.owner)
            items = [self._build_document(job) for job in jobs]
            if arguments.get("status"):
                items = [item for item in items if item["status"] == arguments["status"]]
            return 200, {"items": items, "nextCursor": None}
        if operation_id == "getImageBuild":
            job = await self.database.get_job(arguments["buildId"], identity.owner)
            if job is None or job.kind != "image_build":
                raise Problem(404, "Not found", "Image build was not found")
            return 200, self._build_document(job)
        if operation_id == "cancelImageBuild":
            if not await self.database.cancel_job(arguments["buildId"], identity.owner):
                raise Problem(404, "Not found", "Image build was not found")
            job = await self.database.get_job(arguments["buildId"], identity.owner)
            assert job is not None
            return 202, self._build_document(job)
        if operation_id == "listManagedImages":
            return 200, {
                "items": await self.database.list("image", identity.owner),
                "nextCursor": None,
            }
        if operation_id == "getManagedImage":
            return 200, await self.required("image", arguments["imageId"], identity)
        if operation_id == "deleteManagedImage":
            image = await self.required("image", arguments["imageId"], identity)
            if image.get("activeInstanceReferences"):
                raise Problem(409, "Image in use", "Active instances reference this image")
            await self.database.delete("image", image["id"], identity.owner)
            return 202, {"status": "succeeded"}

        if operation_id in {"createChatCompletion", "createCompletion"}:
            if not self.settings.inference_api_key:
                raise Problem(
                    503,
                    "Inference unavailable",
                    "EDITH_INFERENCE_API_KEY is not configured",
                )
            path = "/chat/completions" if operation_id == "createChatCompletion" else "/completions"
            async with httpx.AsyncClient(timeout=300) as client:
                http_response = await client.post(
                    self.settings.inference_base_url.rstrip("/") + path,
                    headers={"Authorization": f"Bearer {self.settings.inference_api_key}"},
                    json=body,
                )
                http_response.raise_for_status()
                return http_response.status_code, http_response.json()

        if operation_id == "provisionUserInstance":
            job_id = self._id("job")
            await self.database.enqueue(job_id, "provision", identity.owner, body)
            job = await self.database.get_job(job_id, identity.owner)
            assert job is not None
            return 202, self._provision_document(job)
        if operation_id == "getProvisioningJob":
            job = await self.database.get_job(arguments["jobId"], identity.owner)
            if job is None or job.kind != "provision":
                raise Problem(404, "Not found", "Provisioning job was not found")
            return 200, self._provision_document(job)
        if operation_id == "createInstance":
            runtime = body.get("runtime") or {}
            managed = runtime.get("managedImageId")
            if runtime.get("kind") in {"container", "kubernetes"} and not (
                managed or runtime.get("image")
            ):
                raise Problem(422, "Image required", "This runtime requires image or managedImageId")
            request = {
                "owner": body["owner"],
                "name": body["name"],
                **({"image": {"managedImageId": managed}} if managed else {}),
                "runtime": runtime,
                "bootstrap": body.get("bootstrap") or {},
                "labels": body.get("labels") or {},
            }
            job_id = self._id("job")
            await self.database.enqueue(job_id, "provision", identity.owner, request)
            return 202, {
                "id": job_id,
                "instanceId": "pending",
                "action": "create",
                "status": "queued",
                "createdAt": now(),
            }
        if operation_id == "listInstances":
            items = await self.database.list("instance", identity.owner)
            if arguments.get("status"):
                items = [item for item in items if item.get("status") == arguments["status"]]
            if arguments.get("poolId"):
                items = [item for item in items if item.get("poolId") == arguments["poolId"]]
            return 200, {"items": items, "nextCursor": None}
        if operation_id == "getInstance":
            return 200, await self._instance(arguments["instanceId"], identity)
        if operation_id == "updateInstance":
            instance = await self._instance(arguments["instanceId"], identity)
            expected = (arguments.get("headers") or {}).get("If-Match")
            if expected != instance["revision"]:
                raise Problem(
                    412, "Revision mismatch", "If-Match does not match the instance revision"
                )
            labels = {**(instance.get("labels") or {}), **(body.get("labels") or {})}
            if body.get("runtime"):
                runtime = {**instance["runtime"], **body["runtime"]}
                if runtime.get("kind") != instance["runtime"].get("kind"):
                    raise Problem(
                        422,
                        "Runtime kind is immutable",
                        "Create a new instance to migrate between runtime providers",
                    )
                managed_image_id = runtime.get("managedImageId")
                image_reference = runtime.get("image")
                if isinstance(managed_image_id, str):
                    image = await self.required("image", managed_image_id, identity)
                    image_reference = image["immutableReference"]
                if runtime.get("kind") in {"container", "kubernetes"} and not image_reference:
                    raise Problem(
                        422, "Image required", "runtime.image or runtime.managedImageId is required"
                    )
                provider = self.runtimes.get(str(runtime["kind"]))
                artifact = await provider.provision(
                    instance["id"], image_reference, runtime, labels
                )
                instance.update(
                    runtime=runtime,
                    runtimeIdentity=artifact.identity,
                    connection=artifact.connection,
                )
            instance.update({key: value for key, value in body.items() if key != "runtime"})
            instance["labels"] = labels
            instance["revision"] = str(int(instance["revision"]) + 1)
            instance["updatedAt"] = now()
            await self.database.put("instance", instance["id"], identity.owner, instance)
            return 200, instance
        if operation_id == "getInstanceConnection":
            instance = await self._instance(arguments["instanceId"], identity)
            return 200, instance["connection"]
        if operation_id in {"getInstanceCapabilities", "getInstanceRuntimeCapabilities"}:
            instance = await self._instance(arguments["instanceId"], identity)
            return 200, {
                "instanceId": instance["id"],
                "facadeVersion": "0.3.1",
                "upstreamContract": "gateway-contract.openrpc.json",
                "transports": ["http", "sse", "json_rpc", "websocket"],
                "nativeMethods": list(HERMES_RPC_METHODS),
                "contracts": [{"kind": "openrpc", "version": "1"}],
                "domains": {
                    "production": True,
                    "buildkit": True,
                    **{kind: True for kind in self.runtimes.kinds},
                },
            }
        if operation_id == "changeInstanceState":
            instance = await self._instance(arguments["instanceId"], identity)
            action = arguments["action"]
            if action in {"start", "resume", "restart", "reconcile"}:
                provider = self.runtimes.for_identity(instance["runtimeIdentity"])
                if action == "restart":
                    await provider.scale(instance["runtimeIdentity"], 0)
                await provider.scale(instance["runtimeIdentity"], 1)
                instance.update(status="ready", desiredState="running", updatedAt=now())
            elif action in {"stop", "suspend", "drain"}:
                provider = self.runtimes.for_identity(instance["runtimeIdentity"])
                await provider.scale(instance["runtimeIdentity"], 0)
                instance.update(status="stopped", desiredState="stopped", updatedAt=now())
            else:
                raise Problem(422, "Unsupported action", f"Unsupported lifecycle action: {action}")
            await self.database.put("instance", instance["id"], identity.owner, instance)
            return 202, {
                "id": self._id("op"),
                "instanceId": instance["id"],
                "action": action,
                "status": "succeeded",
                "createdAt": now(),
                "completedAt": now(),
            }
        if operation_id == "deleteInstance":
            instance = await self._instance(arguments["instanceId"], identity)
            await self.runtimes.for_identity(instance["runtimeIdentity"]).delete(
                instance["runtimeIdentity"],
                str(arguments.get("retainData", "false")).lower() == "true",
            )
            await self.database.delete("instance", instance["id"], identity.owner)
            return 202, {
                "id": self._id("op"),
                "instanceId": instance["id"],
                "action": "delete",
                "status": "succeeded",
                "createdAt": now(),
                "completedAt": now(),
            }

        if operation_id == "createProfile":
            instance_id = arguments["instanceId"]
            gateway_response = await self._native(instance_id, identity, "profiles.create", body)
            profile_id = self._id("profile")
            profile = {
                **body,
                "id": profile_id,
                "instanceId": instance_id,
                "path": (gateway_response.get("result") or {}).get(
                    "path", f"/opt/data/profiles/{body['name']}"
                ),
                "status": "ready",
                "native": gateway_response.get("result"),
                "createdAt": now(),
            }
            await self.database.put("profile", profile_id, identity.owner, profile)
            return 201, profile
        if operation_id == "listProfiles":
            profiles = await self.database.list("profile", identity.owner)
            return 200, {
                "items": [p for p in profiles if p["instanceId"] == arguments["instanceId"]]
            }
        if operation_id in {"getProfile", "updateProfile", "deleteProfile"}:
            profile = await self.required("profile", arguments["profileId"], identity)
            if profile["instanceId"] != arguments["instanceId"]:
                raise Problem(404, "Not found", "Profile does not belong to this instance")
            if operation_id == "updateProfile":
                await self._native(
                    profile["instanceId"],
                    identity,
                    "profiles.configure",
                    {"name": profile["name"], **body},
                )
                profile.update(body)
                await self.database.put("profile", profile["id"], identity.owner, profile)
                return 200, profile
            if operation_id == "deleteProfile":
                await self.database.delete("profile", profile["id"], identity.owner)
                return 204, None
            return 200, profile

        if operation_id == "invokeHermesRpc":
            return 200, await self._native(
                arguments["instanceId"], identity, body["method"], body.get("params")
            )

        if operation_id == "createSession":
            gateway_response = await self._native(
                arguments["instanceId"], identity, "session.create", body
            )
            result = gateway_response.get("result") or {}
            session_id = str(result.get("session_id") or result.get("id") or self._id("session"))
            session = {
                **body,
                **result,
                "id": session_id,
                "instanceId": arguments["instanceId"],
                "profileId": arguments["profileId"],
                "status": result.get("status", "idle"),
                "createdAt": now(),
                "updatedAt": now(),
            }
            await self.database.put("session", session_id, identity.owner, session)
            return 201, session
        if operation_id == "listSessions":
            sessions = await self.database.list("session", identity.owner)
            return 200, {
                "items": [
                    item
                    for item in sessions
                    if item["instanceId"] == arguments["instanceId"]
                    and item["profileId"] == arguments["profileId"]
                ],
                "nextCursor": None,
            }
        if operation_id == "getSession":
            return 200, await self.required("session", arguments["sessionId"], identity)
        if operation_id == "submitTurn":
            content = body["content"]
            params = {
                "session_id": arguments["sessionId"],
                "text": content if isinstance(content, str) else json.dumps(content),
                "profile": arguments["profileId"],
            }
            gateway_response = await self._native(
                arguments["instanceId"], identity, "prompt.submit", params
            )
            turn_id = self._id("turn")
            turn = {
                "id": turn_id,
                "sessionId": arguments["sessionId"],
                "status": "completed",
                "output": (gateway_response.get("result") or {}).get("output", []),
                "native": gateway_response.get("result"),
                "createdAt": now(),
                "completedAt": now(),
            }
            await self.database.put("turn", turn_id, identity.owner, turn)
            return 202, turn
        if operation_id == "getTurn":
            return 200, await self.required("turn", arguments["turnId"], identity)
        if operation_id == "actOnTurn":
            method = "session.interrupt" if body.get("type") == "stop" else "session.steer"
            gateway_response = await self._native(
                arguments["instanceId"],
                identity,
                method,
                {"session_id": arguments["sessionId"], **body},
            )
            return 202, gateway_response.get("result") or gateway_response
        if operation_id == "actOnSession":
            method = "session." + body["type"]
            gateway_response = await self._native(
                arguments["instanceId"],
                identity,
                method,
                {"session_id": arguments["sessionId"], **body},
            )
            return 200, gateway_response.get("result") or gateway_response
        if operation_id == "deleteSession":
            await self._native(
                arguments["instanceId"],
                identity,
                "session.delete",
                {"session_id": arguments["sessionId"]},
            )
            await self.database.delete("session", arguments["sessionId"], identity.owner)
            return 204, None

        if operation_id == "createToolBundle":
            return 201, await self._create_resource("tool_bundle", "bundle", body, identity)
        if operation_id == "listToolBundles":
            return 200, {
                "items": await self.database.list("tool_bundle", identity.owner),
                "nextCursor": None,
            }
        if operation_id == "getToolBundle":
            return 200, await self.required("tool_bundle", arguments["bundleId"], identity)
        if operation_id == "replaceToolBundle":
            current = await self.required("tool_bundle", arguments["bundleId"], identity)
            updated = {
                **body,
                "id": current["id"],
                "createdAt": current["createdAt"],
                "updatedAt": now(),
            }
            await self.database.put("tool_bundle", current["id"], identity.owner, updated)
            return 200, updated
        if operation_id == "deleteToolBundle":
            await self.database.delete("tool_bundle", arguments["bundleId"], identity.owner)
            return 204, None
        if operation_id == "createToolBinding":
            bundle = await self.required("tool_bundle", body["bundleId"], identity)
            scope = body["scope"]
            instance = await self._instance(scope["instanceId"], identity)
            binding = await self._create_resource(
                "tool_binding",
                "binding",
                {**body, "status": "pending", "bridgeToken": secrets.token_urlsafe(48)},
                identity,
            )
            if bundle["transport"] == "callback":
                if not self.settings.public_base_url:
                    raise Problem(
                        503, "Tool bridge unavailable", "EDITH_PUBLIC_BASE_URL is required"
                    )
                url = f"{self.settings.public_base_url.rstrip('/')}/internal/mcp/{binding['id']}"
                params = {
                    "name": f"edith-{binding['id']}",
                    "transport": "streamable_http",
                    "url": url,
                    "headers": {"Authorization": f"Bearer {binding['bridgeToken']}"},
                }
            else:
                server = await self.required("mcp_server", bundle["mcpServerId"], identity)
                params = server
            await self.gateway.invoke(instance["connection"], "mcp.servers.add", params)
            await self.gateway.invoke(instance["connection"], "mcp.reload", {})
            binding["status"] = "active"
            await self.database.put("tool_binding", binding["id"], identity.owner, binding)
            public = dict(binding)
            public.pop("bridgeToken", None)
            return 201, public
        if operation_id == "listToolBindings":
            items = await self.database.list("tool_binding", identity.owner)
            for item in items:
                item.pop("bridgeToken", None)
            return 200, {"items": items, "nextCursor": None}
        if operation_id == "getToolBinding":
            value = await self.required("tool_binding", arguments["bindingId"], identity)
            value.pop("bridgeToken", None)
            return 200, value
        if operation_id == "deleteToolBinding":
            await self.database.delete("tool_binding", arguments["bindingId"], identity.owner)
            return 204, None
        if operation_id == "createMcpServer":
            return 201, await self._create_resource(
                "mcp_server", "mcp", {**body, "status": "ready"}, identity
            )
        if operation_id == "listMcpServers":
            return 200, {
                "items": await self.database.list("mcp_server", identity.owner),
                "nextCursor": None,
            }
        if operation_id == "getMcpServer":
            return 200, await self.required("mcp_server", arguments["serverId"], identity)
        if operation_id == "replaceMcpServer":
            current = await self.required("mcp_server", arguments["serverId"], identity)
            updated = {
                **body,
                "id": current["id"],
                "status": "ready",
                "createdAt": current["createdAt"],
            }
            await self.database.put("mcp_server", current["id"], identity.owner, updated)
            return 200, updated
        if operation_id == "deleteMcpServer":
            await self.database.delete("mcp_server", arguments["serverId"], identity.owner)
            return 204, None
        if operation_id == "actOnMcpServer":
            server = await self.required("mcp_server", arguments["serverId"], identity)
            action = body["type"]
            if action == "test" and server["transport"] in {"streamable_http", "sse"}:
                async with httpx.AsyncClient(timeout=15) as client:
                    response = await client.get(server["url"])
                    server["status"] = "ready" if response.status_code < 500 else "failed"
            elif action == "reload":
                server["status"] = "connecting"
            elif action == "begin_oauth":
                server["status"] = "needs_auth"
            await self.database.put("mcp_server", server["id"], identity.owner, server)
            return 200, {"id": server["id"], "status": server["status"], "action": action}
        if operation_id == "executeToolCall":
            bundles = await self.database.list("tool_bundle", identity.owner)
            execution_bundle: dict[str, Any] | None = None
            for candidate in bundles:
                names = {tool["name"] for tool in candidate.get("tools") or []}
                if candidate.get("transport") == "callback" and body["tool"] in names:
                    execution_bundle = candidate
                    break
            if execution_bundle is None:
                raise Problem(404, "Tool not found", "No callback bundle provides this tool")
            callback = execution_bundle["callback"]
            headers: dict[str, str] = {}
            if callback.get("secretRef"):
                safe = re.sub(r"[^A-Za-z0-9_.-]", "_", callback["secretRef"])
                secret_file = Path("/var/run/secrets/edith-callback") / safe
                if not secret_file.is_file():
                    raise Problem(503, "Tool unavailable", "Callback secret is not mounted")
                headers["Authorization"] = "Bearer " + secret_file.read_text().strip()
            async with httpx.AsyncClient(timeout=callback.get("timeoutSeconds", 60)) as client:
                http_response = await client.post(callback["url"], json=body, headers=headers)
                http_response.raise_for_status()
                return 200, http_response.json()

        if operation_id == "createPool":
            pool = await self._create_resource(
                "pool",
                "pool",
                {**body, "status": "reconciling", "currentSize": 0, "readySize": 0},
                identity,
            )
            await self._enqueue_pool_instances(pool, int(body.get("desiredSize", 0)), identity)
            return 201, await self._pool_view(pool, identity)
        if operation_id == "listPools":
            pools = await self.database.list("pool", identity.owner)
            return 200, {"items": [await self._pool_view(pool, identity) for pool in pools]}
        if operation_id == "getPool":
            pool = await self.required("pool", arguments["poolId"], identity)
            return 200, await self._pool_view(pool, identity)
        if operation_id == "updatePool":
            pool = await self.required("pool", arguments["poolId"], identity)
            pool = await self._pool_view(pool, identity)
            pool.update(body)
            desired = int(pool.get("desiredSize", 0))
            instances = [
                item
                for item in await self.database.list("instance", identity.owner)
                if item.get("poolId") == pool["id"]
            ]
            pending = len(pool.get("provisioningJobs") or [])
            if desired > len(instances) + pending:
                await self._enqueue_pool_instances(
                    pool, desired - len(instances) - pending, identity
                )
            elif desired < len(instances):
                for instance in instances[desired:]:
                    await self.runtimes.for_identity(instance["runtimeIdentity"]).delete(
                        instance["runtimeIdentity"], retain_data=False
                    )
                    await self.database.delete("instance", instance["id"], identity.owner)
            await self.database.put("pool", pool["id"], identity.owner, pool)
            return 200, await self._pool_view(pool, identity)
        if operation_id == "deletePool":
            pool = await self.required("pool", arguments["poolId"], identity)
            instances = [
                item
                for item in await self.database.list("instance", identity.owner)
                if item.get("poolId") == pool["id"]
            ]
            for instance in instances:
                await self.runtimes.for_identity(instance["runtimeIdentity"]).delete(
                    instance["runtimeIdentity"], retain_data=False
                )
                await self.database.delete("instance", instance["id"], identity.owner)
            await self.database.delete("pool", pool["id"], identity.owner)
            return 204, None
        if operation_id == "acquireInstanceLease":
            pool = await self.required("pool", arguments["poolId"], identity)
            instances = [
                item
                for item in await self.database.list("instance", identity.owner)
                if item.get("poolId") == pool["id"] and item.get("status") == "ready"
            ]
            leases = await self.database.list("lease", identity.owner)
            active_instance_ids = {
                item["instanceId"]
                for item in leases
                if item.get("poolId") == pool["id"]
                and datetime.fromisoformat(item["expiresAt"].replace("Z", "+00:00"))
                > datetime.now(timezone.utc)
            }
            available = [item for item in instances if item["id"] not in active_instance_ids]
            if not available:
                raise Problem(
                    503, "Pool exhausted", "No ready instance is available", retryable=True
                )
            sticky_key = body.get("stickyKey")
            if sticky_key:
                position = int(hashlib.sha256(sticky_key.encode()).hexdigest(), 16) % len(available)
                instance = available[position]
            else:
                instance = available[0]
            lease_profile_id: str | None = None
            profile_request = body.get("profile")
            if isinstance(profile_request, dict) and profile_request.get("profileId"):
                lease_profile_id = profile_request["profileId"]
                await self.required("profile", lease_profile_id, identity)
            elif isinstance(profile_request, dict):
                gateway_response = await self._native(
                    instance["id"], identity, "profiles.create", profile_request
                )
                profile = await self._create_resource(
                    "profile",
                    "profile",
                    {
                        **profile_request,
                        "instanceId": instance["id"],
                        "path": (gateway_response.get("result") or {}).get(
                            "path", f"/opt/data/profiles/{profile_request['name']}"
                        ),
                        "status": "ready",
                    },
                    identity,
                )
                lease_profile_id = profile["id"]
            lease = await self._create_resource(
                "lease",
                "lease",
                {
                    **body,
                    "poolId": pool["id"],
                    "instanceId": instance["id"],
                    "profileId": lease_profile_id,
                    "connection": instance["connection"],
                    "expiresAt": (
                        datetime.now(timezone.utc)
                        + timedelta(seconds=int(body.get("ttlSeconds", 900)))
                    ).isoformat(),
                },
                identity,
            )
            return 201, lease
        if operation_id == "releaseInstanceLease":
            await self.database.delete("lease", arguments["leaseId"], identity.owner)
            return 204, None

        raise Problem(501, "Not implemented", f"Production handler missing for {operation_id}")

    async def _create_resource(
        self,
        kind: str,
        prefix: str,
        body: dict[str, Any],
        identity: Identity,
    ) -> dict[str, Any]:
        resource_id = self._id(prefix)
        value = {**body, "id": resource_id, "createdAt": now()}
        await self.database.put(kind, resource_id, identity.owner, value)
        return value

    async def _enqueue_pool_instances(
        self, pool: dict[str, Any], count: int, identity: Identity
    ) -> None:
        if count <= 0:
            return
        template = pool["template"]
        runtime = template["runtime"]
        managed_image_id = runtime.get("managedImageId")
        if runtime.get("kind") in {"container", "kubernetes"} and not (
            managed_image_id or runtime.get("image")
        ):
            raise Problem(
                422,
                "Image required",
                "Container pool templates require runtime.image or managedImageId",
            )
        jobs = list(pool.get("provisioningJobs") or [])
        offset = len(jobs)
        for index in range(count):
            job_id = self._id("job")
            request = {
                "owner": identity.document(),
                "name": f"{pool['name']}-{offset + index}",
                **({"image": {"managedImageId": managed_image_id}} if managed_image_id else {}),
                "runtime": {**runtime, "poolId": pool["id"]},
                "bootstrap": template.get("bootstrap") or {},
                "labels": {**(template.get("labels") or {}), "edith.pool": pool["id"]},
            }
            await self.database.enqueue(job_id, "provision", identity.owner, request)
            jobs.append(job_id)
        pool["provisioningJobs"] = jobs
        await self.database.put("pool", pool["id"], identity.owner, pool)

    async def _pool_view(self, pool: dict[str, Any], identity: Identity) -> dict[str, Any]:
        instances = [
            item
            for item in await self.database.list("instance", identity.owner)
            if item.get("poolId") == pool["id"]
        ]
        unfinished: list[str] = []
        for job_id in pool.get("provisioningJobs") or []:
            job = await self.database.get_job(job_id, identity.owner)
            if job is not None and job.status in {"queued", "running"}:
                unfinished.append(job_id)
        desired = int(pool.get("desiredSize", 0))
        ready = sum(item.get("status") == "ready" for item in instances)
        pool.update(
            currentSize=len(instances),
            readySize=ready,
            status="ready" if ready >= desired and not unfinished else "reconciling",
            provisioningJobs=unfinished,
        )
        await self.database.put("pool", pool["id"], identity.owner, pool)
        return pool
