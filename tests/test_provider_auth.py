from __future__ import annotations

import asyncio
import inspect
import json
from types import SimpleNamespace
from typing import get_type_hints

import httpx
import pytest
import respx
from edith_hermes_control_plane.app import create_app
from edith_hermes_control_plane.config import Settings
from edith_hermes_control_plane.database import Database
from edith_hermes_control_plane.gateway import HermesGateway
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from edith_hermes import AsyncEdithHermes, Hermes, ProviderLoginError
from edith_hermes.errors import ConflictError, NotFoundError, RemoteError
from edith_hermes.generated.resources import ProviderResource


@pytest.fixture
async def auth_system(tmp_path):
    """Real SDK/HTTP transport/control plane/gateway; scripted native auth protocol.

    No user credentials or real issuer login endpoints are touched.
    """
    native = FastAPI()
    state = SimpleNamespace(
        flows={},
        calls=[],
        credentials={},
        errors={},
        count=0,
        status={
            "logged_in": False,
            "token_preview": "secret-preview",
            "access_token": "secret-access",
            "refresh_token": "secret-refresh",
        },
    )

    @native.api_route("/{path:path}", methods=["GET", "POST", "DELETE"])
    async def handle(path: str, request: Request):
        profile = request.query_params["profile"]
        assert request.headers["authorization"] == "Bearer runtime-secret"
        state.calls.append((request.method, "/" + path, profile))
        if path in state.errors:
            code, value = state.errors[path]
            return JSONResponse(value, status_code=code)
        if path == "api/providers/oauth":
            return {
                "providers": [
                    {
                        "id": "openai-codex",
                        "name": "OpenAI Codex",
                        "flow": "device_code",
                        "disconnectable": True,
                        "status": {**state.status, "logged_in": profile in state.credentials},
                    },
                    {
                        "id": "nous",
                        "name": "Nous",
                        "flow": "device_code",
                        "disconnectable": True,
                        "status": state.status,
                    },
                    {
                        "id": "external-plugin",
                        "name": "External",
                        "flow": "external",
                        "cli_command": "hermes auth add external-plugin",
                        "disconnectable": False,
                        "status": {},
                    },
                ]
            }
        if path.endswith("/start"):
            state.count += 1
            sid = f"native-{state.count}"
            state.flows[sid] = {"status": "pending", "profile": profile}
            return {
                "session_id": sid,
                "flow": "device_code",
                "user_code": "ABCD-EFGH",
                "verification_url": "https://auth.example/device",
                "expires_in": 900,
                "poll_interval": 3,
                "device_auth_id": "secret-device-id",
                "access_token": "secret-access",
            }
        if "/poll/" in path:
            sid = path.rsplit("/", 1)[-1]
            flow = state.flows.get(sid)
            if flow is None:
                return JSONResponse({"detail": "gone"}, status_code=404)
            assert flow["profile"] == profile
            if flow.get("sequence"):
                flow["status"] = flow["sequence"].pop(0)
            if flow["status"] == "approved":
                state.credentials[profile] = "secret-refresh"
            return {
                "status": flow["status"],
                "error_message": "secret-in-native-error",
                "access_token": "secret-access",
            }
        if path.startswith("api/providers/oauth/sessions/"):
            state.flows.pop(path.rsplit("/", 1)[-1], None)
            return {"ok": True}
        if path == "api/credentials/pool":
            return {
                "providers": [
                    {
                        "provider": "openai-codex",
                        "entries": [
                            {
                                "id": "account-a",
                                "index": 1,
                                "label": profile,
                                "auth_type": "oauth",
                                "source": "manual:device_code",
                                "priority": 0,
                                "request_count": 4,
                                "has_refresh": True,
                                "last_status": 401,
                                "token_preview": "secret-preview",
                                "access_token": "secret-access",
                                "refresh_token": "secret-refresh",
                            }
                        ],
                    }
                ]
            }
        if path.startswith("api/credentials/pool/"):
            return {"ok": True, "count": 0, "hints": ["secret-in-hint"]}
        if request.method == "DELETE":
            state.credentials.pop(profile, None)
            return {"ok": True}
        return JSONResponse({"detail": "Unknown"}, status_code=404)

    gateway = HermesGateway()
    await gateway.client.aclose()
    gateway.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=native))
    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'auth.db'}",
        enabled_runtime_providers=["external"],
        auth_mode="static",
        allow_insecure_dev_auth=True,
        dev_tokens={
            "alice": {"tenantId": "tenant", "subjectId": "alice"},
            "bob": {"tenantId": "tenant", "subjectId": "bob"},
        },
    )
    app = create_app(settings, gateway=gateway, start_worker=False)
    async with app.router.lifespan_context(app):
        db = app.state.database
        owner = ("tenant", "alice")
        for instance_id in ("i1", "i2"):
            await db.put(
                "instance",
                instance_id,
                owner,
                {
                    "id": instance_id,
                    "status": "ready",
                    "connection": {
                        "transports": [{"kind": "websocket", "url": "ws://native/api/ws"}],
                        "authorization": {"scheme": "bearer", "token": "runtime-secret"},
                    },
                },
            )
        for profile_id, name, instance_id in (
            ("p1", "Adam", "i1"),
            ("p2", "Anas", "i1"),
            ("p3", "Other", "i2"),
        ):
            await db.put(
                "profile",
                profile_id,
                owner,
                {"id": profile_id, "name": name, "instanceId": instance_id},
            )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://sdk"
        ) as http:
            sdk = AsyncEdithHermes.remote(base_url="http://sdk", token="alice", http_client=http)
            hermes = Hermes(sdk)
            yield SimpleNamespace(
                hermes=hermes,
                sdk=sdk,
                db=db,
                owner=owner,
                state=state,
                http=http,
                provider=hermes.instances("i1").profiles("p1").providers("openai-codex"),
            )


async def test_login_approval_and_profile_scope(auth_system, monkeypatch):
    s = auth_system
    monkeypatch.setattr(
        "edith_hermes.provider_auth.webbrowser.open",
        lambda *_: pytest.fail("Browser opened without permission"),
    )
    login = await s.provider.login()
    assert login.user_code == "ABCD-EFGH"
    assert login.verification_url == "https://auth.example/device"
    assert login.status == "pending"
    assert login.info["pollInterval"] == 3
    s.state.flows["native-1"]["sequence"] = ["pending", "approved"]
    approved = await login.wait(poll_interval=0.001)
    assert approved["status"] == login.status == "approved"
    assert set(s.state.credentials) == {"adam"}
    assert (await s.provider.status())["status"]["state"] == "authenticated"
    assert not (await s.hermes.instances("i1").profiles("p2").providers("openai-codex").status())[
        "status"
    ]["loggedIn"]
    await s.provider.disconnect()
    assert not s.state.credentials
    assert all(call[2] in {"adam", "anas"} for call in s.state.calls)


async def test_redaction_public_and_registry(auth_system):
    s = auth_system
    provider = await s.provider.status()
    login = await s.provider.login()
    poll = await login.get()
    accounts = await s.provider.accounts.list()
    removal = await s.provider.accounts(1).remove()
    records = await s.db.list("provider_login", s.owner)
    assert "secret-" not in json.dumps([provider, login.info, poll, accounts, removal, records])
    assert accounts["items"][0]["label"] == "adam"
    assert accounts["items"][0]["lastStatus"] == 401
    # A 401 is not sufficient evidence of issuer-side revocation.
    assert accounts["items"][0]["validity"] == "unknown"
    assert "/api/credentials/pool/openai-codex/1" in s.state.calls[-1]
    assert "nativeSessionId" not in poll


@pytest.mark.parametrize(
    "status,expected,code",
    [
        ("denied", "denied", "authorization_denied"),
        ("expired", "expired", "authorization_expired"),
        ("error", "failed", "authorization_failed"),
        ("cancelled", "cancelled", "cancelled"),
    ],
)
async def test_failure_states_raise_typed_errors(auth_system, status, expected, code):
    s = auth_system
    login = await s.provider.login()
    s.state.flows["native-1"]["status"] = status
    with pytest.raises(ProviderLoginError) as failed:
        await login.wait(poll_interval=0.001)
    assert failed.value.login["status"] == expected
    assert failed.value.login["errorCode"] == code
    assert "secret-" not in str(failed.value)
    assert (await login.wait(raise_on_failure=False))["status"] == expected


async def test_timeout_is_not_cancel_and_cancel_is_terminal(auth_system):
    s = auth_system
    login = await s.provider.login()
    with pytest.raises(TimeoutError):
        await login.wait(timeout=0)
    assert "native-1" in s.state.flows
    assert (await login.cancel())["status"] == "cancelled"
    assert not s.state.flows
    calls = len(s.state.calls)
    assert (await login.get())["status"] == "cancelled"
    assert (await login.cancel())["status"] == "cancelled"
    assert len(s.state.calls) == calls


async def test_approved_login_cannot_be_cancelled(auth_system):
    s = auth_system
    login = await s.provider.login()
    s.state.flows["native-1"]["status"] = "approved"
    with pytest.raises(ConflictError):
        await login.cancel()
    assert "adam" in s.state.credentials


async def test_runtime_restart_expires_login(auth_system):
    s = auth_system
    login = await s.provider.login()
    s.state.flows.clear()
    result = await login.get()
    assert result["status"] == "expired"
    assert result["errorCode"] == "runtime_session_lost"


async def test_elapsed_ttl_stops_native_worker(auth_system):
    s = auth_system
    login = await s.provider.login()
    row = await s.db.get("provider_login", login.id, s.owner)
    row["expiresAt"] = "2000-01-01T00:00:00Z"
    await s.db.put("provider_login", login.id, s.owner, row)
    assert (await login.get())["status"] == "expired"
    assert not s.state.flows


async def test_idempotency_and_reattach_across_cp_adapters(auth_system):
    s = auth_system
    first = await s.provider.login(idempotency_key="same-request")
    second = await s.provider.login(idempotency_key="same-request")
    assert first.id == second.id and s.state.count == 1
    # New resource handle has no in-memory instructions, but reads the durable registry.
    attached = s.provider.logins(first.id)
    with pytest.raises(RuntimeError):
        _ = attached.user_code
    assert (await attached.get())["userCode"] == first.user_code
    assert get_type_hints(s.provider.login)["return"] is type(first)


@pytest.mark.parametrize(
    "instance,profile,provider",
    [
        ("i1", "p2", "openai-codex"),
        ("i2", "p3", "openai-codex"),
        ("i1", "p1", "nous"),
        ("i2", "p1", "openai-codex"),
    ],
)
async def test_login_scope_cannot_be_overridden(auth_system, instance, profile, provider):
    s = auth_system
    login = await s.provider.login()
    other = s.hermes.instances(instance).profiles(profile).providers(provider).logins(login.id)
    calls = len(s.state.calls)
    with pytest.raises(NotFoundError):
        await other.get()
    with pytest.raises(NotFoundError):
        await other.cancel()
    assert len(s.state.calls) == calls


async def test_owner_isolation(auth_system):
    s = auth_system
    login = await s.provider.login()
    response = await s.http.get(
        f"/v1/instances/i1/profiles/p1/providers/openai-codex/logins/{login.id}",
        headers={"Authorization": "Bearer bob"},
    )
    assert response.status_code == 404


async def test_http_query_and_body_cannot_override_profile_scope(auth_system):
    s = auth_system
    path = "/v1/instances/i1/profiles/p1/providers/openai-codex/logins"
    headers = {"Authorization": "Bearer alice", "Idempotency-Key": "scope-request-123"}
    for url, body in (
        (path + "?profileId=p2", None),
        (path, {"profileId": "p2", "api_key": "secret-input"}),
    ):
        response = await s.http.post(url, json=body, headers=headers)
        assert response.status_code == 422
        assert "secret-input" not in response.text
    assert s.state.count == 0
    assert not await s.db.list("provider_login", s.owner)


async def test_external_providers_are_discoverable_not_auto_logged_in(auth_system):
    s = auth_system
    catalog = await s.hermes.instances("i1").profiles("p1").providers.list()
    external = next(row for row in catalog["items"] if row["id"] == "external-plugin")
    assert not external["loginSupported"] and not external["disconnectSupported"]
    assert external["cliCommand"] == "hermes auth add external-plugin"
    for call in (
        s.hermes.instances("i1").profiles("p1").providers("external-plugin").login,
        s.hermes.instances("i1").profiles("p1").providers("external-plugin").disconnect,
    ):
        with pytest.raises(RemoteError) as error:
            await call()
        assert error.value.status == 501
    assert s.state.count == 0


@pytest.mark.parametrize(
    "code,expected", [(401, 502), (403, 502), (404, 501), (400, 422), (500, 502)]
)
async def test_native_failures_are_sanitized(auth_system, code, expected):
    s = auth_system
    s.state.errors["api/providers/oauth"] = (code, {"detail": "secret-access-token"})
    with pytest.raises(RemoteError) as error:
        await s.provider.status()
    assert error.value.status == expected
    assert "secret-access-token" not in str(error.value)
    assert "secret-access-token" not in json.dumps(error.value.body)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ({"expires_at": 1, "logged_in": True}, "expired"),
        ({"revoked": True, "logged_in": False}, "revoked"),
        ({"error": "secret-auth-error"}, "unknown"),
    ],
)
async def test_credential_state_is_explicit_without_guessing(auth_system, raw, expected):
    s = auth_system
    s.state.status.update(raw)
    assert (await s.provider.status())["status"]["state"] == expected


@pytest.mark.parametrize("timeout,interval", [(-1, 1), (1, 0), (1, -1)])
async def test_login_wait_validates_options(auth_system, timeout, interval):
    login = await auth_system.provider.login()
    with pytest.raises(ValueError):
        await login.wait(timeout=timeout, poll_interval=interval)


async def test_browser_is_explicit_and_safe(auth_system, monkeypatch):
    opened = []
    monkeypatch.setattr(
        "edith_hermes.provider_auth.webbrowser.open", lambda url: opened.append(url) or True
    )
    login = await auth_system.provider.login(open_browser=True)
    assert opened == [login.verification_url]
    info = login.info
    info["verificationUrl"] = "javascript:alert(1)"
    login._remember(info)
    with pytest.raises(ValueError):
        await login.open_browser()
    assert len(opened) == 1


async def test_login_registry_cleanup_and_terminal_compare_and_set(auth_system):
    s = auth_system
    login = await s.provider.login()
    row = await s.db.get("provider_login", login.id, s.owner)
    other_db = Database(s.db.engine.url.render_as_string(hide_password=False))
    try:
        cancelled = {**row, "status": "cancelled", "errorCode": "cancelled"}
        await other_db.save_provider_login(login.id, s.owner, cancelled)
        results = await asyncio.gather(
            *(s.db.save_provider_login(login.id, s.owner, row) for _ in range(8))
        )
        assert all(result["status"] == "cancelled" for result in results)
        assert (await login.get())["status"] == "cancelled"
        await s.db.delete_runtime_tree(s.owner, instance_id="i1", profile_id="p1")
        assert not await s.db.list("provider_login", s.owner)
    finally:
        await other_db.close()


async def test_gateway_basic_auth_cookie_reuse_and_prefix():
    gateway = HermesGateway()
    connection = {
        "transports": [{"kind": "websocket", "url": "wss://native/hermes/api/ws"}],
        "authorization": {"scheme": "dashboard_password", "username": "user", "password": "secret"},
    }
    try:
        with respx.mock:
            catalog = respx.get("https://native/hermes/api/providers/oauth").mock(
                side_effect=[
                    httpx.Response(401),
                    httpx.Response(200, json={"providers": []}),
                    httpx.Response(200, json={"providers": []}),
                ]
            )
            login = respx.post("https://native/hermes/auth/password-login").respond(
                200, json={"ok": True}, headers={"set-cookie": "session=owned; Path=/"}
            )
            for _ in range(2):
                response = await gateway.dashboard_request(
                    connection, "GET", "/api/providers/oauth", profile="Adam"
                )
                assert response.status_code == 200
            assert login.call_count == 1
            assert catalog.calls[-1].request.url.params["profile"] == "Adam"
            assert catalog.calls[-1].request.headers["cookie"] == "session=owned"
            await gateway.forget(connection)
            assert not gateway._dashboard_clients
    finally:
        await gateway.close()


async def test_gateway_http_bridge_transport_auth():
    gateway = HermesGateway()
    try:
        with respx.mock:
            route = respx.get("http://bridge:8081/dashboard/api/providers/oauth").respond(
                200, json={"providers": []}
            )
            await gateway.dashboard_request(
                {
                    "transports": [{"kind": "http", "url": "http://bridge:8081"}],
                    "authorization": {"scheme": "bearer", "token": "bridge-token"},
                },
                "GET",
                "/api/providers/oauth",
                profile="Anas",
            )
            assert route.calls[0].request.headers["authorization"] == "Bearer bridge-token"
            assert route.calls[0].request.url.params["profile"] == "Anas"
    finally:
        await gateway.close()


def test_public_provider_login_annotations_and_index_validation():
    assert "open_browser" in inspect.signature(ProviderResource.login).parameters
    get_type_hints(ProviderResource.login)
