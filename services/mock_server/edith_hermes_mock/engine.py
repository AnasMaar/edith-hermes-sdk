"""Semantic mock implementation for core SDK workflows."""

from __future__ import annotations

import hashlib
import itertools
from datetime import datetime, timezone
from typing import Any

from .state import Owner, StateStore


class MockProblem(Exception):
    def __init__(self, status: int, title: str, detail: str):
        self.status = status
        self.payload = {
            "type": "about:blank",
            "title": title,
            "status": status,
            "detail": detail,
        }
        super().__init__(detail)


class MockEngine:
    def __init__(self, store: StateStore):
        self.store = store
        self._counter = itertools.count(1)

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def identifier(self, prefix: str) -> str:
        return f"{prefix}_{next(self._counter):06d}"

    @staticmethod
    def owner_document(owner: Owner) -> dict[str, str]:
        return {"tenantId": owner[0], "subjectId": owner[1]}

    def require_owner(self, body: dict[str, Any], owner: Owner) -> None:
        requested = body.get("owner")
        if requested is None:
            return
        if (requested.get("tenantId"), requested.get("subjectId")) != owner:
            raise MockProblem(403, "Forbidden", "The resource owner must match the bearer identity")

    def required(self, kind: str, resource_id: str, owner: Owner) -> dict[str, Any]:
        value = self.store.get(kind, resource_id, owner)
        if value is None:
            raise MockProblem(404, "Not found", f"{kind} {resource_id} was not found")
        return value

    async def handle(
        self,
        operation_id: str,
        arguments: dict[str, Any],
        owner: Owner,
    ) -> tuple[int, Any]:
        body = arguments.get("body") or {}
        if isinstance(body, dict):
            self.require_owner(body, owner)

        if operation_id == "createImageRecipe":
            return 201, self._create(
                "recipe", "recipe", body, owner, recipeDigest=self._digest(body)
            )
        if operation_id == "listImageRecipes":
            return 200, {"items": self.store.list("recipe", owner), "nextCursor": None}
        if operation_id == "getImageRecipe":
            return 200, self.required("recipe", arguments["recipeId"], owner)
        if operation_id == "deleteImageRecipe":
            self.store.delete("recipe", arguments["recipeId"], owner)
            return 204, None

        if operation_id == "startImageBuild":
            build = self._create("build", "build", body, owner, status="queued", progress=0)
            return 202, build
        if operation_id == "listImageBuilds":
            return 200, {"items": self.store.list("build", owner), "nextCursor": None}
        if operation_id == "getImageBuild":
            return 200, self._complete_build(arguments["buildId"], owner)
        if operation_id == "cancelImageBuild":
            build = self.required("build", arguments["buildId"], owner)
            build.update(status="cancelled", completedAt=self.now())
            self.store.put("build", build["id"], owner, build)
            return 202, build
        if operation_id == "listManagedImages":
            return 200, {"items": self.store.list("image", owner), "nextCursor": None}
        if operation_id == "getManagedImage":
            return 200, self.required("image", arguments["imageId"], owner)
        if operation_id == "deleteManagedImage":
            image = self.required("image", arguments["imageId"], owner)
            if image.get("activeInstanceReferences", 0):
                raise MockProblem(
                    409, "Image in use", "Active instances still reference this image"
                )
            self.store.delete("image", image["id"], owner)
            return 202, {"status": "queued"}

        if operation_id == "provisionUserInstance":
            job = self._create("provision", "job", body, owner, phase="queued")
            return 202, job
        if operation_id == "getProvisioningJob":
            return 200, self._complete_provision(arguments["jobId"], owner)

        if operation_id == "createInstance":
            instance = self._instance(body, owner)
            return 202, {
                "id": self.identifier("op"),
                "instanceId": instance["id"],
                "action": "create",
                "status": "succeeded",
                "createdAt": self.now(),
                "completedAt": self.now(),
            }
        if operation_id == "listInstances":
            return 200, {"items": self.store.list("instance", owner), "nextCursor": None}
        if operation_id == "getInstance":
            return 200, self.required("instance", arguments["instanceId"], owner)
        if operation_id == "updateInstance":
            instance = self.required("instance", arguments["instanceId"], owner)
            instance.update(body)
            instance["updatedAt"] = self.now()
            self.store.put("instance", instance["id"], owner, instance)
            return 200, instance
        if operation_id == "deleteInstance":
            instance_id = arguments["instanceId"]
            self.required("instance", instance_id, owner)
            self.store.delete("instance", instance_id, owner)
            return 202, self._operation(instance_id, "delete")
        if operation_id == "changeInstanceState":
            instance = self.required("instance", arguments["instanceId"], owner)
            action = arguments["action"]
            instance["status"] = (
                "ready" if action in {"start", "restart", "reconcile"} else "stopped"
            )
            instance["desiredState"] = "running" if instance["status"] == "ready" else "stopped"
            instance["updatedAt"] = self.now()
            self.store.put("instance", instance["id"], owner, instance)
            return 202, self._operation(instance["id"], action)
        if operation_id == "getInstanceConnection":
            return 200, self._connection(arguments["instanceId"])
        if operation_id in {"getInstanceCapabilities", "getInstanceRuntimeCapabilities"}:
            instance_id = arguments["instanceId"]
            self.required("instance", instance_id, owner)
            return 200, {
                "instanceId": instance_id,
                "facadeVersion": "0.3.1",
                "upstreamContract": "gateway-contract.openrpc.json",
                "transports": ["http", "sse", "json_rpc"],
                "nativeMethods": [],
                "contracts": [{"kind": "openrpc", "version": "1"}],
                "domains": {"mock": True},
            }

        if operation_id == "createProfile":
            profile = self._profile(arguments["instanceId"], body, owner)
            return 201, profile
        if operation_id == "listProfiles":
            items = [
                item
                for item in self.store.list("profile", owner)
                if item["instanceId"] == arguments["instanceId"]
            ]
            return 200, {"items": items}
        if operation_id in {"getProfile", "updateProfile", "deleteProfile"}:
            profile_id = arguments["profileId"]
            profile = self.required("profile", profile_id, owner)
            if operation_id == "updateProfile":
                profile.update(body)
                self.store.put("profile", profile_id, owner, profile)
                return 200, profile
            if operation_id == "deleteProfile":
                self.store.delete("profile", profile_id, owner)
                return 204, None
            return 200, profile

        if operation_id == "createSession":
            session = self._create(
                "session",
                "session",
                body,
                owner,
                instanceId=arguments["instanceId"],
                profileId=arguments["profileId"],
                status="idle",
            )
            return 201, session
        if operation_id == "listSessions":
            items = [
                item
                for item in self.store.list("session", owner)
                if item["instanceId"] == arguments["instanceId"]
                and item["profileId"] == arguments["profileId"]
            ]
            return 200, {"items": items, "nextCursor": None}
        if operation_id in {"getSession", "deleteSession", "actOnSession"}:
            session_id = arguments["sessionId"]
            session = self.required("session", session_id, owner)
            if operation_id == "deleteSession":
                self.store.delete("session", session_id, owner)
                return 204, None
            if operation_id == "actOnSession":
                session["status"] = "closed" if body.get("type") == "close" else "idle"
                self.store.put("session", session_id, owner, session)
            return 200, session
        if operation_id == "submitTurn":
            self.required("session", arguments["sessionId"], owner)
            turn = self._create(
                "turn",
                "turn",
                body,
                owner,
                sessionId=arguments["sessionId"],
                status="completed",
                output=[],
            )
            return 202, turn
        if operation_id == "getTurn":
            return 200, self.required("turn", arguments["turnId"], owner)
        if operation_id == "actOnTurn":
            turn = self.required("turn", arguments["turnId"], owner)
            if body.get("type") == "stop":
                turn["status"] = "stopped"
                self.store.put("turn", turn["id"], owner, turn)
            return 202, turn

        if operation_id == "invokeHermesRpc":
            return 200, {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "mock": True,
                    "method": body.get("method"),
                    "params": body.get("params"),
                },
            }

        return await self._generic(operation_id, arguments, body, owner)

    async def _generic(
        self, operation_id: str, arguments: dict[str, Any], body: dict[str, Any], owner: Owner
    ) -> tuple[int, Any]:
        lower = operation_id.lower()
        kinds = {
            "pool": "pool",
            "lease": "lease",
            "toolbundle": "tool_bundle",
            "toolbinding": "tool_binding",
            "mcpserver": "mcp_server",
        }
        kind = next((value for token, value in kinds.items() if token in lower), "fixture")
        if lower.startswith("create") or lower.startswith("acquire"):
            value = self._create(kind, kind, body, owner, status="ready")
            return 201, value
        if lower.startswith("list"):
            return 200, {"items": self.store.list(kind, owner), "nextCursor": None}
        if lower.startswith("delete") or lower.startswith("release"):
            identifier = next(
                (value for key, value in arguments.items() if key.lower().endswith("id")), None
            )
            if identifier:
                self.store.delete(kind, str(identifier), owner)
            return 204, None
        return 200, {"mock": True, "operationId": operation_id, "arguments": arguments}

    def _create(
        self, kind: str, prefix: str, body: dict[str, Any], owner: Owner, **extra: Any
    ) -> dict[str, Any]:
        value = dict(body)
        value.update(extra)
        value.setdefault("id", self.identifier(prefix))
        value.setdefault("owner", self.owner_document(owner))
        value.setdefault("createdAt", self.now())
        self.store.put(kind, value["id"], owner, value)
        return value

    @staticmethod
    def _digest(value: Any) -> str:
        import json

        return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

    def _complete_build(self, build_id: str, owner: Owner) -> dict[str, Any]:
        build = self.required("build", build_id, owner)
        if build["status"] not in {"succeeded", "cancelled", "failed"}:
            image = self._create(
                "image",
                "image",
                {},
                owner,
                repository="mock.local/edith/hermes",
                digest=self._digest(build),
                immutableReference="mock.local/edith/hermes@" + self._digest(build),
                platforms=["linux/amd64"],
                verification={
                    "status": "passed",
                    "criticalVulnerabilities": 0,
                    "highVulnerabilities": 0,
                },
                activeInstanceReferences=0,
            )
            build.update(
                status="succeeded", progress=100, imageId=image["id"], completedAt=self.now()
            )
            self.store.put("build", build_id, owner, build)
        return build

    def _complete_provision(self, job_id: str, owner: Owner) -> dict[str, Any]:
        job = self.required("provision", job_id, owner)
        if job["phase"] != "ready":
            source = job.get("image", {})
            managed_image_id = source.get("managedImageId")
            if not managed_image_id:
                build = self._create(
                    "build", "build", source.get("build", {}), owner, status="queued", progress=0
                )
                build = self._complete_build(build["id"], owner)
                managed_image_id = build["imageId"]
                job["imageBuildId"] = build["id"]
            instance = self._instance(
                {
                    "owner": self.owner_document(owner),
                    "name": job.get("name", "provisioned-hermes"),
                    "runtime": {**job.get("runtime", {}), "managedImageId": managed_image_id},
                    "bootstrap": job.get("bootstrap", {}),
                    "labels": job.get("labels", {}),
                },
                owner,
            )
            profile_data = job.get("bootstrap", {}).get("profile") or {"name": "default"}
            profile = self._profile(instance["id"], profile_data, owner)
            job.update(
                phase="ready",
                managedImageId=managed_image_id,
                instanceId=instance["id"],
                profileId=profile["id"],
                connection=self._connection(instance["id"]),
                completedAt=self.now(),
            )
            self.store.put("provision", job_id, owner, job)
        return job

    def _instance(self, body: dict[str, Any], owner: Owner) -> dict[str, Any]:
        timestamp = self.now()
        instance = self._create(
            "instance",
            "instance",
            body,
            owner,
            status="ready",
            desiredState="running",
            revision="1",
            updatedAt=timestamp,
        )
        instance["runtimeIdentity"] = {
            "provider": instance.get("runtime", {}).get("kind", "kubernetes"),
            "podName": f"mock-{instance['id']}",
            "serviceDnsName": f"{instance['id']}.mock.local",
        }
        self.store.put("instance", instance["id"], owner, instance)
        return instance

    def _profile(self, instance_id: str, body: dict[str, Any], owner: Owner) -> dict[str, Any]:
        return self._create(
            "profile",
            "profile",
            body,
            owner,
            instanceId=instance_id,
            path=f"/opt/data/profiles/{body.get('name', 'default')}",
            status="ready",
        )

    def _connection(self, instance_id: str) -> dict[str, Any]:
        return {
            "instanceId": instance_id,
            "transports": [{"kind": "http", "url": f"http://{instance_id}.mock.local:9119"}],
            "authorization": {"scheme": "bearer", "token": "mock-runtime-token"},
            "expiresAt": "2099-01-01T00:00:00Z",
        }

    def _operation(self, instance_id: str, action: str) -> dict[str, Any]:
        return {
            "id": self.identifier("op"),
            "instanceId": instance_id,
            "action": action,
            "status": "succeeded",
            "createdAt": self.now(),
            "completedAt": self.now(),
        }
