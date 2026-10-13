import json

import httpx
import pytest

from edith_hermes import AsyncHermesDesktop


@pytest.mark.asyncio
async def test_profile_scope_and_wire_contract():
    requests = []
    def receive(request):
        requests.append(request)
        if request.url.path.endswith("/runs"):
            return httpx.Response(200, json={"runs": [{"id": "run-1"}]})
        return httpx.Response(200, json={"id": "job-1", "profile": "door"})
    async with httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(receive)) as http:
        client = AsyncHermesDesktop.remote(base_url="http://hermes", profile="family", token="secret", http_client=http)
        door = client.for_profile("door")
        await door.cron.update("job-1", {"prompt": "Hello", "model": None})
        assert await door.cron.runs("job-1") == [{"id": "run-1"}]
        assert client.profile == "family"
        assert all(r.url.params["profile"] == "door" for r in requests)
        assert all(r.headers["authorization"] == "Bearer secret" for r in requests)
        assert json.loads(requests[0].content) == {"updates": {"prompt": "Hello", "model": None}}
        await door.aclose()
        assert not http.is_closed


@pytest.mark.asyncio
async def test_uncertain_mutation_is_not_replayed():
    attempts = 0
    def receive(request):
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("Reply lost", request=request)
    async with httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(receive)) as http:
        client = AsyncHermesDesktop.remote(base_url="http://hermes", profile="family", http_client=http)
        with pytest.raises(httpx.ReadTimeout):
            await client.cron.trigger("job-1")
        assert attempts == 1


@pytest.mark.asyncio
async def test_discovery_uses_real_operations_and_encoded_ids():
    requests = []
    def receive(request):
        requests.append(request)
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json={"paths": {"/api/cron/jobs": {"get": {}, "parameters": []}}})
        return httpx.Response(200, json={"id": "job"})
    async with httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(receive)) as http:
        client = AsyncHermesDesktop.remote(base_url="http://hermes", profile="family", http_client=http)
        assert (await client.capabilities())["operations"] == ["GET /api/cron/jobs"]
        await client.cron.get("a/b ?#")
        assert b"a%2Fb%20%3F%23" in requests[-1].url.raw_path
        with pytest.raises(ValueError):
            await client.cron.get("..")


@pytest.mark.parametrize("profile", ["", "all"])
def test_concrete_profile_required(profile):
    with pytest.raises(ValueError):
        AsyncHermesDesktop.remote(base_url="http://hermes", profile=profile)


@pytest.mark.asyncio
async def test_history_checks_returned_owner_and_bounds():
    def receive(request):
        assert request.url.params["profile"] == "family"
        assert request.url.params["inline_images"] == "false"
        return httpx.Response(200, json={"profile": "door", "messages": []})
    async with httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(receive)) as http:
        client = AsyncHermesDesktop.remote(base_url="http://hermes", profile="family", http_client=http)
        with pytest.raises(ValueError, match="another profile"):
            await client.sessions.messages("same-id")
        with pytest.raises(ValueError, match="between 1 and 500"):
            await client.sessions.messages("same-id", limit=501)
