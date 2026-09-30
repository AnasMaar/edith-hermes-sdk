"""Production semantics behind the generated SDK operation catalog."""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import uuid
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

from edith_hermes.generated.operations import HERMES_RPC_METHODS, PROFILE_RPC_METHODS

from .auth import Identity
from .config import Settings
from .database import Database, DurableJob
from .gateway import HermesGateway
from .profiles import configure, create_params
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
    def _binding_server_name(binding: dict[str, Any]) -> str:
        # Existing databases registered the full binding ID; preserve that name
        # for removal/OAuth rather than silently renaming a live native server.
        return str(binding.get("nativeServerName") or "edith-" + binding["id"])

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

    async def _profile_name(self, instance_id: str, profile_id: str, identity: Identity) -> str:
        profile = await self.required("profile", profile_id, identity)
        if profile["instanceId"] != instance_id:
            raise Problem(404, "Not found", "Profile does not belong to this instance")
        return str(profile["name"])

    async def _native(
        self, instance_id: str, identity: Identity, method: str, params: Any = None
    ) -> dict[str, Any]:
        instance = await self._instance(instance_id, identity)
        if instance.get("status") != "ready":
            raise Problem(409, "Instance unavailable", "The Hermes instance is not ready")
        return await self.gateway.invoke(instance["connection"], method, params)

    async def _session(self, arguments: dict[str, Any], identity: Identity) -> dict[str, Any]:
        session = await self.required("session", arguments["sessionId"], identity)
        if (
            session["instanceId"] != arguments["instanceId"]
            or session["profileId"] != arguments["profileId"]
        ):
            raise Problem(404, "Not found", "Session does not belong to this profile")
        return session

    async def _reload_bound_tools(
        self,
        session: dict[str, Any],
        identity: Identity,
        *,
        initialize: bool = False,
    ) -> None:
        bindings = await self.database.list("tool_binding", identity.owner)
        relevant = [
            binding
            for binding in bindings
            if (
                binding.get("status") == "active"
                and binding.get("scope", {}).get("instanceId") == session["instanceId"]
                and binding.get("scope", {}).get("profileId") == session["profileId"]
            )
        ]
        if relevant:
            native_id = session.get("nativeSessionId") or session["id"]
            revision = self._digest([native_id, sorted(binding["id"] for binding in relevant)])
            if initialize:
                if session.get("toolBindingRevision") == revision:
                    return
                # Native session.create AND session.activate are lazy. The
                # read-only process.list waits for agent construction, unlike
                # activate/info/status. Reload can then discover this profile
                # and refresh its actual agent snapshot before the first prompt.
                await self._native(
                    session["instanceId"],
                    identity,
                    "process.list",
                    {"session_id": native_id},
                )
            response = await self._native(
                session["instanceId"],
                identity,
                "reload.mcp",
                {"session_id": session.get("nativeSessionId") or session["id"], "confirm": True},
            )
            if (response.get("result") or {}).get("status") == "confirm_required":
                raise Problem(502, "Tool reload incomplete", "Hermes did not reload profile tools")
            if initialize:
                session["toolBindingRevision"] = revision
                await self.database.put("session", session["id"], identity.owner, session)

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
                raise Problem(
                    422, "Image required", "This runtime requires image or managedImageId"
                )
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
                "facadeVersion": "0.4.0",
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
                if instance["runtimeIdentity"].get("provider") == "container":
                    port = instance["runtimeIdentity"]["port"]
                    instance["connection"]["transports"] = [
                        {"kind": "websocket", "url": f"ws://127.0.0.1:{port}/api/ws"}
                    ]
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
            forget = getattr(self.gateway, "forget", None)
            if forget is not None and instance.get("connection"):
                with suppress(Exception):
                    await forget(instance["connection"])
            await self.database.delete_runtime_tree(identity.owner, instance_id=instance["id"])
            image_id = instance.get("runtime", {}).get("managedImageId")
            if image_id:
                linked_image = await self.database.get("image", image_id, identity.owner)
                if linked_image:
                    linked_image["activeInstanceReferences"] = max(
                        0, int(linked_image.get("activeInstanceReferences", 0)) - 1
                    )
                    await self.database.put("image", image_id, identity.owner, linked_image)
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
            gateway_response = await self._native(
                instance_id, identity, "profiles.create", create_params(body)
            )
            instance = await self._instance(instance_id, identity)
            await configure(self.gateway, instance["connection"], body)
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
                instance = await self._instance(profile["instanceId"], identity)
                await configure(
                    self.gateway, instance["connection"], {**body, "name": profile["name"]}
                )
                profile.update(body)
                await self.database.put("profile", profile["id"], identity.owner, profile)
                return 200, profile
            if operation_id == "deleteProfile":
                if profile["name"] == "default":
                    raise Problem(
                        409, "Protected profile", "The native default profile cannot be deleted"
                    )
                response = await self._native(
                    profile["instanceId"],
                    identity,
                    "cli.exec",
                    {
                        "argv": ["profile", "delete", profile["name"], "--yes"],
                    },
                )
                result = response.get("result") or {}
                if result.get("blocked") or result.get("code") != 0:
                    raise Problem(
                        502,
                        "Profile deletion failed",
                        "Hermes did not confirm native deletion; registry entry retained",
                    )
                await self.database.delete_runtime_tree(
                    identity.owner,
                    instance_id=profile["instanceId"],
                    profile_id=profile["id"],
                )
                return 204, None
            return 200, profile

        if operation_id == "invokeHermesRpc":
            params = dict(body.get("params") or {})
            if arguments.get("profileId"):
                name = await self._profile_name(
                    arguments["instanceId"], arguments["profileId"], identity
                )
                if body["method"] in PROFILE_RPC_METHODS:
                    params["profile"] = name
            return 200, await self._native(
                arguments["instanceId"], identity, body["method"], params
            )

        if operation_id == "createSession":
            if body.get("environment") or body.get("toolBindingIds"):
                raise Problem(
                    422,
                    "Unsupported session override",
                    "Per-session environment/tool bindings are not implemented; use a dedicated profile",
                )
            params = {
                k: v
                for k, v in body.items()
                if k
                not in {
                    "toolBindingIds",
                    "metadata",
                    "environment",
                    "workingDirectory",
                    "resumeNativeSessionId",
                }
            }
            if "workingDirectory" in body:
                params["cwd"] = body["workingDirectory"]
            params["profile"] = await self._profile_name(
                arguments["instanceId"], arguments["profileId"], identity
            )
            method = "session.create"
            if body.get("resumeNativeSessionId"):
                if body.get("workingDirectory") or body.get("title"):
                    raise Problem(
                        422,
                        "Invalid resume options",
                        "Resume does not accept title or workingDirectory",
                    )
                method = "session.resume"
                params["session_id"] = body["resumeNativeSessionId"]
            gateway_response = await self._native(arguments["instanceId"], identity, method, params)
            result = gateway_response.get("result") or {}
            if not (result.get("session_id") or result.get("id")):
                raise Problem(502, "Invalid runtime response", "Hermes did not return a session ID")
            session_id = str(result.get("session_id") or result["id"])
            session = {
                **body,
                **result,
                "id": session_id,
                "nativeSessionId": session_id,
                "instanceId": arguments["instanceId"],
                "profileId": arguments["profileId"],
                "status": result.get("status", "idle"),
                "createdAt": now(),
                "updatedAt": now(),
            }
            await self.database.put("session", session_id, identity.owner, session)
            # Native session construction can snapshot tools before this profile's
            # MCP servers enter the process-wide registry. Discovery alone is not
            # sufficient: refresh the live agent before exposing a usable session.
            await self._reload_bound_tools(session, identity)
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
            return 200, await self._session(arguments, identity)
        if operation_id == "submitTurn":
            if body.get("toolBindingIds"):
                raise Problem(
                    422,
                    "Unsupported turn override",
                    "Per-turn tool isolation is not implemented; bind tools to a dedicated profile",
                )
            session = await self.required("session", arguments["sessionId"], identity)
            if (
                session["instanceId"] != arguments["instanceId"]
                or session["profileId"] != arguments["profileId"]
            ):
                raise Problem(404, "Not found", "Session does not belong to this profile")
            await self._reload_bound_tools(session, identity, initialize=True)
            before = await self._native(
                arguments["instanceId"],
                identity,
                "session.events.since",
                {"session_id": session.get("nativeSessionId") or session["id"]},
            )
            content = body["content"]
            params = {
                "session_id": session.get("nativeSessionId") or session["id"],
                "text": content,
                "queued": body.get("mode", "enqueue") == "enqueue",
                "profile": await self._profile_name(
                    arguments["instanceId"], arguments["profileId"], identity
                ),
            }
            gateway_response = await self._native(
                arguments["instanceId"], identity, "prompt.submit", params
            )
            turn_id = self._id("turn")
            turn = {
                "id": turn_id,
                "sessionId": arguments["sessionId"],
                "status": "running",
                "output": (gateway_response.get("result") or {}).get("output", []),
                "native": gateway_response.get("result"),
                "eventCursor": (before.get("result") or {}).get("latest_seq", 0),
                "eventEpoch": (before.get("result") or {}).get("epoch"),
                "createdAt": now(),
            }
            await self.database.put("turn", turn_id, identity.owner, turn)
            return 202, turn
        if operation_id == "getTurn":
            turn = await self.required("turn", arguments["turnId"], identity)
            session = await self.required("session", arguments["sessionId"], identity)
            if (
                turn["sessionId"] != session["id"]
                or session["instanceId"] != arguments["instanceId"]
                or session["profileId"] != arguments["profileId"]
            ):
                raise Problem(404, "Not found", "Turn does not belong to this session/profile")
            if turn["status"] in {"running", "waiting_for_approval"}:
                response = await self._native(
                    arguments["instanceId"],
                    identity,
                    "session.events.since",
                    {
                        "session_id": session.get("nativeSessionId") or session["id"],
                        "last_seen": turn["eventCursor"],
                    },
                )
                replay = response.get("result") or {}
                for event in replay.get("events", []):
                    if event.get("type") == "message.complete":
                        payload = event.get("payload") or {}
                        turn["status"] = (
                            "failed"
                            if payload.get("error") or payload.get("status") == "error"
                            else "stopped"
                            if payload.get("status") == "interrupted"
                            else "completed"
                        )
                        turn["output"] = [{"type": "text", "text": str(payload.get("text", ""))}]
                        turn["nativeCompletion"] = payload
                        turn["completedAt"] = now()
                        break
                if turn["status"] in {"running", "waiting_for_approval"}:
                    turn["status"] = (
                        "waiting_for_approval" if replay.get("open_requests") else "running"
                    )
                    if (
                        replay.get("truncated")
                        or turn.get("eventEpoch")
                        and replay.get("epoch") != turn["eventEpoch"]
                    ):
                        turn["status"] = "failed"
                        turn["error"] = {
                            "title": "Event history unavailable",
                            "detail": "Gateway restarted or event replay was truncated; inspect native session history.",
                        }
                turn["eventCursor"] = replay.get("latest_seq", turn["eventCursor"])
                await self.database.put("turn", turn["id"], identity.owner, turn)
            return 200, turn
        if operation_id == "actOnTurn":
            turn = await self.required("turn", arguments["turnId"], identity)
            session = await self.required("session", arguments["sessionId"], identity)
            if (
                turn["sessionId"] != session["id"]
                or session["instanceId"] != arguments["instanceId"]
                or session["profileId"] != arguments["profileId"]
            ):
                raise Problem(404, "Not found", "Turn does not belong to this session/profile")
            params = {
                "session_id": session.get("nativeSessionId") or session["id"],
                "profile": await self._profile_name(
                    arguments["instanceId"], arguments["profileId"], identity
                ),
            }
            action = body.get("type")
            if action == "stop":
                method = "session.interrupt"
            elif action == "steer":
                method = "session.steer"
                params["text"] = body["content"]
            elif action == "approval":
                method = "approval.respond"
                choices = {"allow_once": "once", "allow_session": "session", "deny": "deny"}
                if body.get("decision") not in choices or not body.get("requestId"):
                    raise Problem(422, "Invalid approval", "Supply a requestId and valid decision")
                params.update(request_id=body["requestId"], choice=choices[body["decision"]])
            else:
                raise Problem(422, "Invalid turn action", "Expected stop, steer or approval")
            gateway_response = await self._native(
                arguments["instanceId"],
                identity,
                method,
                params,
            )
            return 202, gateway_response.get("result") or gateway_response
        if operation_id == "actOnSession":
            session = await self._session(arguments, identity)
            action = body["type"]
            if action not in {
                "resume",
                "activate",
                "close",
                "interrupt",
                "compress",
                "undo",
                "branch",
            }:
                raise Problem(422, "Invalid session action", "Unknown session action")
            if body.get("fromTurnId"):
                raise Problem(
                    422,
                    "Unsupported branch boundary",
                    "Use native.session.branch(count=...) for an explicit message boundary",
                )
            method = "session." + action
            params = {
                "session_id": session.get("nativeSessionId") or session["id"],
                "profile": await self._profile_name(
                    arguments["instanceId"], arguments["profileId"], identity
                ),
            }
            if action == "resume":
                params["session_id"] = session.get("stored_session_id") or params["session_id"]
            gateway_response = await self._native(
                arguments["instanceId"],
                identity,
                method,
                params,
            )
            result = gateway_response.get("result") or {}
            if action == "branch":
                if not result.get("session_id"):
                    raise Problem(
                        502, "Invalid branch response", "Native branch returned no session_id"
                    )
                session = {**session, "id": result["session_id"], "createdAt": now()}
            if result.get("session_id"):
                session["nativeSessionId"] = result["session_id"]
            if result.get("stored_session_id"):
                session["stored_session_id"] = result["stored_session_id"]
            session.update(updatedAt=now(), nativeActionResult=result)
            if action in {"resume", "activate", "branch", "close", "interrupt"}:
                session["status"] = {"close": "closed", "interrupt": "interrupted"}.get(
                    action, "idle"
                )
            await self.database.put("session", session["id"], identity.owner, session)
            if action in {"resume", "branch"}:
                await self._reload_bound_tools(session, identity)
            return 200, session
        if operation_id == "deleteSession":
            session = await self._session(arguments, identity)
            await self._native(
                arguments["instanceId"],
                identity,
                "session.delete",
                {
                    "session_id": session.get("stored_session_id") or session["id"],
                    "profile": await self._profile_name(
                        arguments["instanceId"], arguments["profileId"], identity
                    ),
                },
            )
            await self.database.delete_runtime_tree(
                identity.owner,
                instance_id=arguments["instanceId"],
                profile_id=arguments["profileId"],
                session_id=arguments["sessionId"],
            )
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
            if scope.get("level") != "profile" or not scope.get("profileId"):
                raise Problem(
                    422,
                    "Unsupported tool scope",
                    "Native registration is profile-scoped; use a dedicated profile",
                )
            instance = await self._instance(scope["instanceId"], identity)
            profile_name = await self._profile_name(
                scope["instanceId"], scope["profileId"], identity
            )
            if bundle["transport"] == "callback" and not self.settings.public_base_url:
                raise Problem(503, "Tool bridge unavailable", "EDITH_PUBLIC_BASE_URL is required")
            server = {}
            if bundle["transport"] != "callback":
                server = await self.required("mcp_server", bundle["mcpServerId"], identity)
                if server.get("secretRefs") or body.get("enabledTools") is not None:
                    raise Problem(
                        422,
                        "Unsupported MCP override",
                        "Native MCP secret/filter reconciliation is not implemented; configure native credentials or use a callback bundle",
                    )
            binding = await self._create_resource(
                "tool_binding",
                "binding",
                {**body, "status": "pending", "bridgeToken": secrets.token_urlsafe(48)},
                identity,
            )
            # Native names are mcp__<server>__<tool>, capped at 64 characters.
            # Reserve room for the Python name so tool search retains meaningful
            # words rather than seeing only a long UUID + hashed suffix.
            binding["nativeServerName"] = "edith-" + binding["id"].removeprefix("binding_")[:20]
            await self.database.put("tool_binding", binding["id"], identity.owner, binding)
            if bundle["transport"] == "callback":
                url = f"{self.settings.public_base_url.rstrip('/')}/internal/mcp/{binding['id']}"
                params = {
                    "name": self._binding_server_name(binding),
                    "config": {
                        "transport": "streamable_http",
                        "url": url,
                        "headers": {"Authorization": f"Bearer {binding['bridgeToken']}"},
                    },
                }
            else:
                config = {
                    k: server[k]
                    for k in ("transport", "url", "command", "args", "headers", "auth")
                    if k in server
                }
                if "environment" in server:
                    config["env"] = server["environment"]
                params = {"name": self._binding_server_name(binding), "config": config}
            params = {**params, "profile": profile_name}
            try:
                await self.gateway.invoke(instance["connection"], "mcp.servers.add", params)
                # Existing sessions require reload(session_id), not a profile argument.
                for session in await self.database.list("session", identity.owner):
                    if session["instanceId"] == instance["id"] and (
                        not scope.get("profileId") or session["profileId"] == scope["profileId"]
                    ):
                        await self.gateway.invoke(
                            instance["connection"],
                            "reload.mcp",
                            {
                                "session_id": session.get("nativeSessionId") or session["id"],
                                "confirm": True,
                            },
                        )
            except BaseException:
                # A failed registration must not leave a binding that points to a
                # revoked callback or a bundle the client subsequently removes.
                with suppress(Exception):
                    await self.gateway.invoke(
                        instance["connection"],
                        "mcp.servers.remove",
                        {"name": params["name"], "profile": profile_name},
                    )
                await self.database.delete("tool_binding", binding["id"], identity.owner)
                raise
            binding["status"] = "active"
            await self.database.put("tool_binding", binding["id"], identity.owner, binding)
            public = dict(binding)
            public.pop("bridgeToken", None)
            return 201, public
        if operation_id == "listToolBindings":
            items = await self.database.list("tool_binding", identity.owner)
            items = [
                item
                for item in items
                if all(
                    not arguments.get(key) or item["scope"].get(key) == arguments[key]
                    for key in ("instanceId", "profileId", "sessionId")
                )
            ]
            for item in items:
                item.pop("bridgeToken", None)
            return 200, {"items": items, "nextCursor": None}
        if operation_id == "getToolBinding":
            value = await self.required("tool_binding", arguments["bindingId"], identity)
            value.pop("bridgeToken", None)
            return 200, value
        if operation_id == "deleteToolBinding":
            binding = await self.required("tool_binding", arguments["bindingId"], identity)
            scope = binding["scope"]
            await self._native(
                scope["instanceId"],
                identity,
                "mcp.servers.remove",
                {
                    "name": self._binding_server_name(binding),
                    "profile": await self._profile_name(
                        scope["instanceId"], scope["profileId"], identity
                    ),
                },
            )
            for session in await self.database.list("session", identity.owner):
                if (
                    session["instanceId"] == scope["instanceId"]
                    and session["profileId"] == scope["profileId"]
                ):
                    await self._native(
                        scope["instanceId"],
                        identity,
                        "reload.mcp",
                        {
                            "session_id": session.get("nativeSessionId") or session["id"],
                            "confirm": True,
                        },
                    )
            await self.database.delete("tool_binding", arguments["bindingId"], identity.owner)
            return 204, None
        if operation_id == "createMcpServer":
            return 201, await self._create_resource(
                "mcp_server", "mcp", {**body, "status": "unknown"}, identity
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
            bundles = await self.database.list("tool_bundle", identity.owner)
            bundle_ids = {b["id"] for b in bundles if b.get("mcpServerId") == server["id"]}
            bindings = [
                b
                for b in await self.database.list("tool_binding", identity.owner)
                if b["bundleId"] in bundle_ids
                and b.get("status") == "active"
                and (not body.get("bindingId") or b["id"] == body["bindingId"])
            ]
            if len(bindings) != 1:
                raise Problem(
                    409,
                    "MCP target required",
                    "Bind the server to a profile; supply bindingId when multiple bindings exist",
                )
            binding = bindings[0]
            scope = binding["scope"]
            params = {
                "name": self._binding_server_name(binding),
                "profile": await self._profile_name(
                    scope["instanceId"], scope["profileId"], identity
                ),
            }
            methods = {
                "test": "test",
                "begin_oauth": "oauth.start",
                "poll_oauth": "oauth.poll",
                "complete_oauth": "oauth.callback",
                "cancel_oauth": "oauth.cancel",
            }
            if action == "reload":
                results = []
                for session in await self.database.list("session", identity.owner):
                    if (
                        session["instanceId"] == scope["instanceId"]
                        and session["profileId"] == scope["profileId"]
                    ):
                        results.append(
                            await self._native(
                                scope["instanceId"],
                                identity,
                                "reload.mcp",
                                {"session_id": session.get("nativeSessionId") or session["id"]},
                            )
                        )
                return 200, {
                    "id": server["id"],
                    "action": action,
                    "reloadedSessions": len(results),
                    "results": results,
                }
            if action not in methods:
                raise Problem(422, "Unknown MCP action", str(action))
            if action in {"poll_oauth", "complete_oauth", "cancel_oauth"}:
                if not body.get("sessionId"):
                    raise Problem(
                        422,
                        "OAuth flow required",
                        "sessionId is the OAuth flow ID returned by begin_oauth",
                    )
                params["session_id"] = body["sessionId"]
            if action == "begin_oauth" and body.get("clientRedirectUri"):
                params["client_redirect_uri"] = body["clientRedirectUri"]
            if action == "complete_oauth":
                for wire, native in {
                    "code": "code",
                    "state": "state",
                    "error": "error",
                    "issuer": "iss",
                }.items():
                    if wire in body:
                        params[native] = body[wire]
            response = await self._native(
                scope["instanceId"], identity, "mcp.servers." + methods[action], params
            )
            result = response.get("result") or {}
            if action == "test":
                server["status"] = (
                    "ready"
                    if result.get("ok")
                    else "needs_auth"
                    if result.get("oauth_needed")
                    else "failed"
                )
                server["discoveredTools"] = result.get("tools", [])
            elif action == "begin_oauth":
                server["status"] = "needs_auth" if result.get("ok") else "failed"
            elif action == "poll_oauth":
                server["status"] = {"approved": "ready", "error": "failed"}.get(
                    str(result.get("status")), "needs_auth"
                )
            await self.database.put("mcp_server", server["id"], identity.owner, server)
            return 200, {
                "id": server["id"],
                "status": server["status"],
                "action": action,
                "result": result,
            }
        if operation_id == "executeToolCall":
            bundles = await self.database.list("tool_bundle", identity.owner)
            bindings = await self.database.list("tool_binding", identity.owner)
            target = body.get("target") or {}
            matching = [
                b
                for b in bindings
                if b.get("status") == "active"
                and all(target.get(k) == v for k, v in b["scope"].items() if k != "level")
                and (b.get("enabledTools") is None or body["tool"] in b["enabledTools"])
            ]
            allowed_bundles = {b["bundleId"] for b in matching}
            execution_bundle: dict[str, Any] | None = None
            for candidate in bundles:
                if candidate["id"] not in allowed_bundles:
                    continue
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
            self._validate_pool(body)
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
            self._validate_pool(pool)
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
                if pending:
                    raise Problem(409, "Pool busy", "Wait for provisioning before scaling down")
                leased = {
                    lease["instanceId"]
                    for lease in await self._active_pool_leases(pool["id"], identity)
                }
                removable = [item for item in instances if item["id"] not in leased]
                count = len(instances) - desired
                if len(removable) < count:
                    raise Problem(409, "Pool leased", "Release active leases before scaling down")
                for instance in removable[-count:]:
                    await self.handle("deleteInstance", {"instanceId": instance["id"]}, identity)
            await self.database.put("pool", pool["id"], identity.owner, pool)
            return 200, await self._pool_view(pool, identity)
        if operation_id == "deletePool":
            pool = await self.required("pool", arguments["poolId"], identity)
            pool = await self._pool_view(pool, identity)
            if pool.get("provisioningJobs") or await self._active_pool_leases(pool["id"], identity):
                raise Problem(
                    409,
                    "Pool busy",
                    "Wait for provisioning and release active leases before deletion",
                )
            instances = [
                item
                for item in await self.database.list("instance", identity.owner)
                if item.get("poolId") == pool["id"]
            ]
            for instance in instances:
                await self.handle("deleteInstance", {"instanceId": instance["id"]}, identity)
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
                and not item.get("releasedAt")
                and datetime.fromisoformat(item["expiresAt"].replace("Z", "+00:00"))
                > datetime.now(timezone.utc)
            }
            required_labels = body.get("requiredLabels") or {}
            available = [
                item
                for item in instances
                if item["id"] not in active_instance_ids
                and all(item.get("labels", {}).get(k) == v for k, v in required_labels.items())
            ]
            profile_request = body.get("profile")
            if isinstance(profile_request, dict) and profile_request.get("profileId"):
                requested = await self.required("profile", profile_request["profileId"], identity)
                if not any(item["id"] == requested["instanceId"] for item in instances):
                    raise Problem(
                        404, "Not found", "Profile does not belong to an instance in this pool"
                    )
                available = [item for item in available if item["id"] == requested["instanceId"]]
            if not available:
                raise Problem(
                    503, "Pool exhausted", "No ready instance is available", retryable=True
                )
            sticky_key = body.get("stickyKey")
            if sticky_key:
                available.sort(
                    key=lambda item: hashlib.sha256((sticky_key + item["id"]).encode()).digest()
                )
            else:
                strategy = pool.get("strategy", "round_robin")
                if strategy == "random":
                    offset = secrets.randbelow(len(available))
                    available = available[offset:] + available[:offset]
                elif strategy in {"least_sessions", "least_busy"}:
                    sessions = await self.database.list("session", identity.owner)
                    busy = {
                        turn["sessionId"]
                        for turn in await self.database.list("turn", identity.owner)
                        if turn.get("status") in {"running", "waiting_for_approval"}
                    }
                    available.sort(
                        key=lambda item: sum(
                            s["instanceId"] == item["id"]
                            and (strategy == "least_sessions" or s["id"] in busy)
                            for s in sessions
                        )
                    )
                else:
                    available.sort(
                        key=lambda item: max(
                            (
                                lease.get("createdAt", "")
                                for lease in leases
                                if lease["instanceId"] == item["id"]
                            ),
                            default="",
                        )
                    )
            ttl = body.get("ttlSeconds", 900)
            if not isinstance(ttl, int) or isinstance(ttl, bool) or ttl < 1:
                raise Problem(422, "Invalid TTL", "ttlSeconds must be a positive integer")
            lease_id = self._id("lease")
            expires = datetime.now(timezone.utc) + timedelta(seconds=ttl)
            selected = None
            for candidate in available:
                if await self.database.reserve_lease_slot(
                    candidate["id"], identity.owner, lease_id, expires
                ):
                    selected = candidate
                    break
            if selected is None:
                raise Problem(
                    503, "Pool exhausted", "No ready instance is available", retryable=True
                )
            instance = selected
            try:
                lease_profile_id: str | None = None
                if isinstance(profile_request, dict) and profile_request.get("profileId"):
                    lease_profile_id = profile_request["profileId"]
                elif isinstance(profile_request, dict):
                    _, profile = await self.handle(
                        "createProfile",
                        {"instanceId": instance["id"], "body": profile_request},
                        identity,
                    )
                    lease_profile_id = profile["id"]
                lease = {
                    **body,
                    "id": lease_id,
                    "poolId": pool["id"],
                    "instanceId": instance["id"],
                    "profileId": lease_profile_id,
                    "connection": instance["connection"],
                    "expiresAt": expires.isoformat(),
                    "createdAt": now(),
                }
                await self.database.put("lease", lease_id, identity.owner, lease)
            except BaseException:
                await self.database.release_lease_slot(instance["id"], identity.owner, lease_id)
                raise
            return 201, lease
        if operation_id == "releaseInstanceLease":
            lease = await self.required("lease", arguments["leaseId"], identity)
            if lease["poolId"] != arguments["poolId"]:
                raise Problem(404, "Not found", "Lease does not belong to this pool")
            await self.database.release_lease_slot(lease["instanceId"], identity.owner, lease["id"])
            lease["releasedAt"] = now()
            await self.database.put("lease", arguments["leaseId"], identity.owner, lease)
            return 204, None

        raise Problem(501, "Not implemented", f"Production handler missing for {operation_id}")

    @staticmethod
    def _validate_pool(pool: dict[str, Any]) -> None:
        minimum = pool.get("minimumSize", 0)
        desired = pool.get("desiredSize", minimum)
        maximum = pool.get("maximumSize", max(1, desired))
        if (
            any(not isinstance(v, int) or isinstance(v, bool) for v in (minimum, desired, maximum))
            or not 0 <= minimum <= desired <= maximum
            or maximum < 1
        ):
            raise Problem(
                422,
                "Invalid pool size",
                "Require 0 <= minimumSize <= desiredSize <= maximumSize and maximumSize >= 1",
            )
        pool["desiredSize"] = desired
        if pool.get("strategy", "round_robin") not in {
            "round_robin",
            "random",
            "least_sessions",
            "least_busy",
            "sticky_key",
        }:
            raise Problem(
                422, "Unsupported strategy", "Custom pool schedulers need a concrete adapter"
            )
        if pool.get("kubernetes") or pool.get("idleTtlSeconds"):
            raise Problem(
                422,
                "Unsupported pool automation",
                "StatefulSet mapping and automatic idle eviction are not implemented; use independent runtimes and explicit scaling",
            )

    async def _active_pool_leases(self, pool_id: str, identity: Identity) -> list[dict[str, Any]]:
        return [
            item
            for item in await self.database.list("lease", identity.owner)
            if item["poolId"] == pool_id
            and not item.get("releasedAt")
            and datetime.fromisoformat(item["expiresAt"].replace("Z", "+00:00"))
            > datetime.now(timezone.utc)
        ]

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
