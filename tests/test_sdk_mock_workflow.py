from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from edith_hermes_mock.app import create_app

from edith_hermes import AsyncEdithHermes, AuthenticationError, NotFoundError


def client_for(
    database: Path, token: str = "dev-user-1"
) -> tuple[AsyncEdithHermes, httpx.AsyncClient]:
    app = create_app(database)
    http = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://mock",
        headers={"Authorization": f"Bearer {token}"},
    )
    return AsyncEdithHermes.remote(base_url="http://mock", token=token, http_client=http), http


@pytest.mark.asyncio
async def test_build_provision_session_and_rpc_survive_restart(tmp_path: Path) -> None:
    database = tmp_path / "state.db"
    sdk, http = client_for(database)
    owner = {"tenantId": "dev", "subjectId": "user-1"}

    build = await sdk.images.start_image_build(
        body={
            "owner": owner,
            "source": {
                "recipe": {
                    "owner": owner,
                    "name": "data-runtime",
                    "baseImage": "nousresearch/hermes-agent@sha256:" + "1" * 64,
                }
            },
            "destination": {"repository": "mock.local/user-1/hermes"},
        }
    )
    completed = await sdk.images.get_image_build(build_id=build["id"])
    assert completed["status"] == "succeeded"

    job = await sdk.control_plane.provision_user_instance(
        body={
            "owner": owner,
            "name": "user-1-hermes",
            "image": {"managedImageId": completed["imageId"]},
            "runtime": {"kind": "kubernetes", "poolId": "pool-default"},
            "bootstrap": {"profile": {"name": "default"}},
        }
    )
    ready = await sdk.control_plane.get_provisioning_job(job_id=job["id"])
    assert ready["phase"] == "ready"

    session = await sdk.runtime.create_session(
        instance_id=ready["instanceId"],
        profile_id=ready["profileId"],
        body={"title": "first session"},
    )
    turn = await sdk.runtime.submit_turn(
        instance_id=ready["instanceId"],
        profile_id=ready["profileId"],
        session_id=session["id"],
        body={"content": "hello"},
    )
    assert turn["status"] == "completed"

    rpc = await sdk.gateway.prompt_submit(
        instance_id=ready["instanceId"],
        profile_id=ready["profileId"],
        text="hello",
    )
    assert rpc["result"]["method"] == "prompt.submit"
    await sdk.aclose()
    await http.aclose()

    restarted, restarted_http = client_for(database)
    restored = await restarted.control_plane.get_instance(instance_id=ready["instanceId"])
    assert restored["name"] == "user-1-hermes"
    await restarted.aclose()
    await restarted_http.aclose()


@pytest.mark.asyncio
async def test_owner_isolation(tmp_path: Path) -> None:
    database = tmp_path / "state.db"
    first, first_http = client_for(database, "dev-user-1")
    second, second_http = client_for(database, "dev-user-2")
    owner = {"tenantId": "dev", "subjectId": "user-1"}

    operation = await first.control_plane.create_instance(
        body={
            "owner": owner,
            "name": "private",
            "runtime": {"kind": "container", "image": "example@sha256:" + "2" * 64},
        },
        headers={"Idempotency-Key": "test-owner-isolation"},
    )
    with pytest.raises(NotFoundError):
        await second.control_plane.get_instance(instance_id=operation["instanceId"])

    await first.aclose()
    await second.aclose()
    await first_http.aclose()
    await second_http.aclose()


@pytest.mark.asyncio
async def test_authentication_is_required(tmp_path: Path) -> None:
    app = create_app(tmp_path / "state.db")
    http = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://mock")
    sdk = AsyncEdithHermes.remote(base_url="http://mock", token="invalid", http_client=http)
    with pytest.raises(AuthenticationError):
        await sdk.control_plane.list_instances()
    await sdk.aclose()
    await http.aclose()
