import asyncio

import httpx
import pytest

from edith_hermes import AsyncHermesDesktop
from edith_hermes.errors import AuthenticationError, RemoteError

OPERATION = "GET /api/dashboard/plugins/catalog"
CAPABILITIES = {"reachable": True, "operations": [OPERATION]}


def catalog_row():
    return {
        "name": "catalog-plugin", "description": "A reviewed integration", "repo": "https://github.com/example/plugin",
        "sha": "a" * 40, "sha_short": "aaaaaaa", "tier": "community", "maintainer": "example",
        "requires_hermes": ">=0.22", "platforms": ["win32"], "docs_url": "", "capability_summary": "tools",
        "capabilities": {"provides_tools": ["read"], "provides_hooks": [], "provides_middleware": [], "requires_env": []},
        "installed": True, "installed_sha": "b" * 40, "update_available": True, "runtime_status": "enabled",
        "title": "Catalog plugin", "subdir": "plugin", "known_issues": [], "future_field": "retained",
    }


@pytest.mark.asyncio
async def test_catalog_discovers_exact_native_endpoint_then_reads_authenticated_wire_shape():
    requests = []
    response = {"entries": [catalog_row()], "removed": [{"name": "recalled", "repo": "https://github.com/example/old", "reason": "removed", "date": "2026-10-15"}], "generated_at": "2026-10-15T00:00:00Z"}

    def receive(request):
        requests.append(request)
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json={"paths": {"/api/dashboard/plugins/catalog": {"get": {}}}})
        return httpx.Response(200, json=response)

    async with httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(receive)) as http:
        client = AsyncHermesDesktop.remote(base_url="http://hermes", profile="door", token="test-only-token", http_client=http)
        actual = await client.plugins.catalog()
    assert [request.url.path for request in requests] == ["/openapi.json", "/api/dashboard/plugins/catalog"]
    assert dict(requests[1].url.params) == {"profile": "door"}
    assert all(request.headers["authorization"] == "Bearer test-only-token" for request in requests)
    assert actual == response
    assert actual["entries"][0]["sha"] == "a" * 40
    assert actual["removed"][0]["name"] == "recalled"


@pytest.mark.asyncio
async def test_catalog_can_use_existing_owning_deployment_capability_snapshot():
    requests = []

    def receive(request):
        requests.append(request)
        return httpx.Response(200, json={"entries": [], "removed": [], "generated_at": "now"})

    async with httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(receive)) as http:
        client = AsyncHermesDesktop.remote(base_url="http://hermes", profile="family", http_client=http)
        await client.plugins.catalog(capabilities=CAPABILITIES)
        await client.for_profile("door").plugins.catalog(capabilities=CAPABILITIES)
    assert len(requests) == 2
    assert [dict(request.url.params) for request in requests] == [{"profile": "family"}, {"profile": "door"}]


@pytest.mark.asyncio
@pytest.mark.parametrize("capabilities,status", [
    ({"reachable": True, "operations": []}, 501),
    ({"reachable": True, "operations": ["POST /api/dashboard/plugins/catalog"]}, 501),
    ({"reachable": False, "operations": [OPERATION]}, 503),
])
async def test_unsupported_or_disconnected_service_never_returns_a_successful_empty_catalog(capabilities, status):
    def receive(request):
        pytest.fail("A rejected capability must not invoke the endpoint")

    async with httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(receive)) as http:
        client = AsyncHermesDesktop.remote(base_url="http://hermes", profile="family", http_client=http)
        with pytest.raises(RemoteError) as caught:
            await client.plugins.catalog(capabilities=capabilities)
        assert caught.value.status == status


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_path", ["/openapi.json", "/api/dashboard/plugins/catalog"])
async def test_discovery_and_read_authentication_failure_are_not_empty_inventory_or_retry(failure_path):
    requests = []

    def receive(request):
        requests.append(request)
        if request.url.path == failure_path:
            return httpx.Response(401, json={"detail": "authentication required"})
        return httpx.Response(200, json={"paths": {"/api/dashboard/plugins/catalog": {"get": {}}}})

    async with httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(receive)) as http:
        client = AsyncHermesDesktop.remote(base_url="http://hermes", profile="family", http_client=http)
        with pytest.raises(AuthenticationError):
            await client.plugins.catalog()
    assert len(requests) == (1 if failure_path == "/openapi.json" else 2)


@pytest.mark.asyncio
async def test_native_timeout_is_propagated_without_retry_or_fixture_fallback():
    requests = []

    def receive(request):
        requests.append(request)
        raise httpx.ReadTimeout("native read timed out", request=request)

    async with httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(receive)) as http:
        client = AsyncHermesDesktop.remote(base_url="http://hermes", profile="family", http_client=http)
        with pytest.raises(httpx.ReadTimeout):
            await client.plugins.catalog(capabilities=CAPABILITIES)
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_cancellation_detaches_waiting_read_without_retry():
    entered = asyncio.Event()
    requests = []

    async def receive(request):
        requests.append(request)
        entered.set()
        await asyncio.Future()

    async with httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(receive)) as http:
        client = AsyncHermesDesktop.remote(base_url="http://hermes", profile="family", http_client=http)
        task = asyncio.create_task(client.plugins.catalog(capabilities=CAPABILITIES))
        await entered.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert len(requests) == 1
