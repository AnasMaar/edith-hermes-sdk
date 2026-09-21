from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "services" / "control_plane"))

from edith_hermes_control_plane.app import create_app  # noqa: E402
from edith_hermes_control_plane.config import Settings  # noqa: E402
from edith_hermes_control_plane.database import Database  # noqa: E402
from edith_hermes_control_plane.providers import BuildArtifact, RuntimeArtifact  # noqa: E402

from edith_hermes import AsyncEdithHermes  # noqa: E402


class FakeBuildKit:
    @staticmethod
    def recipe_digest(_: dict[str, Any]) -> str:
        return "sha256:" + "1" * 64

    async def build(self, *_: Any) -> BuildArtifact:
        return BuildArtifact(
            repository="registry.example/hermes",
            digest="sha256:" + "2" * 64,
            immutable_reference="registry.example/hermes@sha256:" + "2" * 64,
            platforms=["linux/amd64"],
            verification={"status": "passed"},
        )


class FakeKubernetes:
    def __init__(self) -> None:
        self.apps: object | None = None

    async def start(self) -> None:
        self.apps = object()

    async def close(self) -> None:
        return None

    async def provision(self, instance_id: str, image: str, *_: Any) -> RuntimeArtifact:
        return RuntimeArtifact(
            identity={
                "provider": "kubernetes",
                "namespace": "test",
                "workloadName": instance_id,
                "image": image,
            },
            connection={
                "instanceId": instance_id,
                "transports": [{"kind": "http", "url": "http://runtime"}],
                "authorization": {"scheme": "none"},
                "expiresAt": "9999-12-31T23:59:59Z",
            },
        )

    async def scale(self, *_: Any) -> None:
        return None

    async def delete(self, *_: Any, **__: Any) -> None:
        return None


class FakeGateway:
    async def close(self) -> None:
        return None

    async def invoke(self, _: Any, method: str, params: Any = None) -> dict[str, Any]:
        if method == "profiles.create":
            return {"jsonrpc": "2.0", "id": 1, "result": {"path": "/opt/data/profiles/default"}}
        if method == "session.create":
            return {"jsonrpc": "2.0", "id": 1, "result": {"session_id": "native-session"}}
        if method == "prompt.submit":
            return {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"output": [{"type": "text", "text": params["text"]}]},
            }
        return {"jsonrpc": "2.0", "id": 1, "result": {"method": method, "params": params}}


async def wait_until(call: Any, field: str, terminal: set[str]) -> dict[str, Any]:
    for _ in range(100):
        value = await call()
        if value[field] in terminal:
            return value
        await asyncio.sleep(0.01)
    raise AssertionError("job did not reach a terminal state")


@pytest.mark.asyncio
async def test_real_control_plane_orchestration_with_provider_fakes(tmp_path: Path) -> None:
    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'production.db'}",
        allow_insecure_dev_auth=True,
        dev_tokens={"test-token": {"tenantId": "tenant", "subjectId": "user"}},
        require_image_scan=False,
        require_image_signature=False,
        worker_poll_seconds=0.01,
        worker_concurrency=1,
        public_base_url="http://control-plane",
    )
    app = create_app(
        settings,
        database=Database(settings.database_url),
        kubernetes=FakeKubernetes(),  # type: ignore[arg-type]
        buildkit=FakeBuildKit(),  # type: ignore[arg-type]
        gateway=FakeGateway(),  # type: ignore[arg-type]
    )
    async with app.router.lifespan_context(app):
        http = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://control-plane",
        )
        sdk = AsyncEdithHermes.remote(
            base_url="http://control-plane",
            token="test-token",
            http_client=http,
        )
        owner = {"tenantId": "tenant", "subjectId": "user"}
        build = await sdk.images.start_image_build(
            body={
                "owner": owner,
                "source": {
                    "recipe": {
                        "owner": owner,
                        "name": "production",
                        "baseImage": "nousresearch/hermes-agent@sha256:" + "0" * 64,
                    }
                },
                "destination": {"repository": "registry.example/hermes"},
            },
            headers={"Idempotency-Key": "production-build-key"},
        )
        duplicate = await sdk.images.start_image_build(
            body={
                "owner": owner,
                "source": {
                    "recipe": {
                        "owner": owner,
                        "name": "production",
                        "baseImage": "nousresearch/hermes-agent@sha256:" + "0" * 64,
                    }
                },
                "destination": {"repository": "registry.example/hermes"},
            },
            headers={"Idempotency-Key": "production-build-key"},
        )
        assert duplicate["id"] == build["id"]
        completed = await wait_until(
            lambda: sdk.images.get_image_build(build_id=build["id"]),
            "status",
            {"succeeded", "failed"},
        )
        assert completed["status"] == "succeeded"

        pool = await sdk.control_plane.create_pool(
            body={
                "name": "production-pool",
                "desiredSize": 1,
                "maximumSize": 2,
                "template": {
                    "runtime": {
                        "kind": "kubernetes",
                        "managedImageId": completed["imageId"],
                    },
                    "bootstrap": {"profile": {"name": "default"}},
                },
            }
        )
        for _ in range(100):
            pool = await sdk.control_plane.get_pool(pool_id=pool["id"])
            if pool["status"] == "ready":
                break
            await asyncio.sleep(0.01)
        assert pool["readySize"] == 1
        lease = await sdk.control_plane.acquire_instance_lease(
            pool_id=pool["id"],
            body={"stickyKey": "user", "ttlSeconds": 60},
        )
        assert lease["instanceId"]
        await sdk.control_plane.release_instance_lease(pool_id=pool["id"], lease_id=lease["id"])

        job = await sdk.control_plane.provision_user_instance(
            body={
                "owner": owner,
                "name": "user-hermes",
                "image": {"managedImageId": completed["imageId"]},
                "runtime": {"kind": "kubernetes"},
                "bootstrap": {"profile": {"name": "default"}},
            }
        )
        ready = await wait_until(
            lambda: sdk.control_plane.get_provisioning_job(job_id=job["id"]),
            "phase",
            {"ready", "failed"},
        )
        assert ready["phase"] == "ready"
        session = await sdk.runtime.create_session(
            instance_id=ready["instanceId"],
            profile_id=ready["profileId"],
            body={"title": "production"},
        )
        turn = await sdk.runtime.submit_turn(
            instance_id=ready["instanceId"],
            profile_id=ready["profileId"],
            session_id=session["id"],
            body={"content": "hello"},
        )
        assert turn["output"][0]["text"] == "hello"

        bundle = await sdk.tools.create_tool_bundle(
            body={
                "name": "ring-tools",
                "transport": "callback",
                "callback": {"url": "https://callback.example/tools"},
                "tools": [
                    {
                        "name": "ring_battery",
                        "description": "Read ring battery",
                        "inputSchema": {"type": "object"},
                    }
                ],
            }
        )
        binding = await sdk.tools.create_tool_binding(
            body={
                "bundleId": bundle["id"],
                "scope": {
                    "level": "profile",
                    "instanceId": ready["instanceId"],
                    "profileId": ready["profileId"],
                },
            }
        )
        found = await app.state.database.find("tool_binding", binding["id"])
        assert found is not None
        _, private_binding = found
        mcp = await http.post(
            f"/internal/mcp/{binding['id']}",
            headers={"Authorization": f"Bearer {private_binding['bridgeToken']}"},
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        )
        assert mcp.json()["result"]["tools"][0]["name"] == "ring_battery"
        await sdk.aclose()
        await http.aclose()
