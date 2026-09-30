"""Horizontally safe durable job worker."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any

from .config import Settings
from .database import Database, DurableJob
from .gateway import HermesGateway
from .profiles import configure, create_params
from .providers import BuildKitProvider, RuntimeRegistry
from .providers.buildkit import BuildCancelled


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobWorker:
    def __init__(
        self,
        database: Database,
        settings: Settings,
        buildkit: BuildKitProvider,
        runtimes: RuntimeRegistry,
        gateway: HermesGateway,
    ):
        self.database = database
        self.settings = settings
        self.buildkit = buildkit
        self.runtimes = runtimes
        self.gateway = gateway
        self.worker_id = str(uuid.uuid4())
        self._stop = asyncio.Event()
        self._tasks: list[asyncio.Task[None]] = []

    def start(self) -> None:
        self._tasks = [
            asyncio.create_task(self._loop(), name=f"job-worker-{index}")
            for index in range(self.settings.worker_concurrency)
        ]

    async def stop(self) -> None:
        self._stop.set()
        # Let idle claim transactions finish before cancellation closes SQLite connections.
        _, pending = await asyncio.wait(self._tasks, timeout=1) if self._tasks else (set(), set())
        for task in pending:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def _loop(self) -> None:
        while not self._stop.is_set():
            job = await self.database.claim_job(self.worker_id)
            if job is None:
                await asyncio.sleep(self.settings.worker_poll_seconds)
                continue
            heartbeat = asyncio.create_task(self._heartbeat(job.job_id))
            try:
                result = await self._execute(job)
                await self.database.finish_job(job.job_id, status="succeeded", result=result)
            except BuildCancelled:
                await self.database.finish_job(job.job_id, status="cancelled")
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                await self.database.append_job_log(job.job_id, f"ERROR: {exc}")
                await self.database.finish_job(
                    job.job_id,
                    status="failed",
                    error={
                        "type": "about:blank",
                        "title": "Job failed",
                        "status": 500,
                        "detail": str(exc),
                    },
                )
            finally:
                heartbeat.cancel()
                await asyncio.gather(heartbeat, return_exceptions=True)

    async def _heartbeat(self, job_id: str) -> None:
        while True:
            await asyncio.sleep(30)
            await self.database.heartbeat_job(job_id, self.worker_id)

    async def _execute(self, job: DurableJob) -> dict[str, Any]:
        if job.kind == "image_build":
            return await self._build(job)
        if job.kind == "provision":
            return await self._provision(job)
        raise RuntimeError(f"Unknown durable job kind: {job.kind}")

    async def _build_image(
        self, owner: tuple[str, str], job_id: str, request: dict[str, Any]
    ) -> dict[str, Any]:
        source = request["source"]
        if "recipeId" in source:
            recipe = await self.database.get("recipe", source["recipeId"], owner)
            if recipe is None:
                raise RuntimeError(f"Image recipe {source['recipeId']} does not exist")
        else:
            recipe = source["recipe"]
        artifact = await self.buildkit.build(
            recipe,
            request["destination"],
            request.get("buildSecretRefs") or [],
            lambda line: self.database.append_job_log(job_id, line),
            lambda: self.database.job_cancel_requested(job_id),
        )
        image_id = "image_" + uuid.uuid4().hex
        image = {
            "id": image_id,
            "owner": {"tenantId": owner[0], "subjectId": owner[1]},
            "repository": artifact.repository,
            "digest": artifact.digest,
            "immutableReference": artifact.immutable_reference,
            "platforms": artifact.platforms,
            "recipeDigest": self.buildkit.recipe_digest(recipe),
            "verification": artifact.verification,
            "activeInstanceReferences": 0,
            "createdAt": now(),
        }
        await self.database.put("image", image_id, owner, image)
        return {"imageId": image_id, "image": image}

    async def _build(self, job: DurableJob) -> dict[str, Any]:
        return await self._build_image((job.tenant_id, job.subject_id), job.job_id, job.payload)

    async def _provision(self, job: DurableJob) -> dict[str, Any]:
        owner = (job.tenant_id, job.subject_id)
        request = job.payload
        source = request.get("image") or {}
        image: dict[str, Any] | None = None
        image_id: str | None = None
        if "managedImageId" in source:
            image = await self.database.get("image", source["managedImageId"], owner)
            if image is None:
                raise RuntimeError("The managed image does not exist or belongs to another owner")
            image_id = image["id"]
        elif "build" in source:
            build_request = {
                "owner": request["owner"],
                "source": {"recipe": source["build"]["recipe"]},
                "destination": {
                    "repository": source["build"]["repository"],
                    "registryCredentialRef": source["build"].get("registryCredentialRef"),
                },
            }
            built = await self._build_image(owner, job.job_id, build_request)
            image = built["image"]
            image_id = built["imageId"]
        runtime = request["runtime"]
        kind = str(runtime.get("kind") or "")
        provider = self.runtimes.get(kind)
        image_reference = image["immutableReference"] if image else runtime.get("image")
        instance_id = "instance_" + uuid.uuid4().hex
        instance = {
            "id": instance_id,
            "owner": request["owner"],
            "name": request["name"],
            "runtime": {
                **runtime,
                **({"managedImageId": image_id} if image_id else {}),
                **({"image": image_reference} if image_reference else {}),
            },
            "status": "provisioning",
            "desiredState": "running",
            "poolId": runtime.get("poolId"),
            "labels": request.get("labels") or {},
            "revision": "1",
            "createdAt": now(),
            "updatedAt": now(),
        }
        await self.database.put("instance", instance_id, owner, instance)
        try:
            artifact = await provider.provision(
                instance_id,
                image_reference,
                runtime,
                request.get("labels") or {},
            )
        except Exception:
            instance.update(status="failed", health={"ready": False, "checkedAt": now()})
            await self.database.put("instance", instance_id, owner, instance)
            raise
        instance.update(
            status="provisioning",
            runtimeIdentity=artifact.identity,
            connection=artifact.connection,
            health={"ready": False, "checkedAt": now()},
            updatedAt=now(),
        )
        await self.database.put("instance", instance_id, owner, instance)
        if image is not None and image_id is not None:
            image["activeInstanceReferences"] = int(image.get("activeInstanceReferences", 0)) + 1
            await self.database.put("image", image_id, owner, image)
        profile_data = (request.get("bootstrap") or {}).get("profile") or {"name": "default"}
        try:
            native = (
                await self.gateway.invoke(
                    artifact.connection, "profiles.create", create_params(profile_data)
                )
                if profile_data["name"] != "default"
                else {"result": {"path": "/opt/data"}}
            )
            await configure(self.gateway, artifact.connection, profile_data)
        except Exception:
            await provider.delete(artifact.identity, retain_data=False)
            instance.update(status="failed", health={"ready": False, "checkedAt": now()})
            await self.database.put("instance", instance_id, owner, instance)
            raise
        native_result = native.get("result") or {}
        profile_id = "profile_" + uuid.uuid4().hex
        profile = {
            **profile_data,
            "id": profile_id,
            "instanceId": instance_id,
            "path": native_result.get("path", f"/opt/data/profiles/{profile_data['name']}"),
            "status": "ready",
            "native": native_result,
            "createdAt": now(),
        }
        await self.database.put("profile", profile_id, owner, profile)
        instance.update(status="ready", health={"ready": True, "checkedAt": now()})
        await self.database.put("instance", instance_id, owner, instance)
        return {
            **({"managedImageId": image_id} if image_id else {}),
            "instanceId": instance_id,
            "profileId": profile_id,
            "connection": artifact.connection,
        }
