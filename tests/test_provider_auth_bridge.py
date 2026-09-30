from __future__ import annotations

import httpx
import pytest
import respx
from edith_hermes_runtime_bridge.app import app


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "api/providers/oauth"),
        ("POST", "api/providers/oauth/openai-codex/start"),
        ("GET", "api/providers/oauth/openai-codex/poll/abc_123-xyz"),
        ("DELETE", "api/providers/oauth/sessions/abc_123-xyz"),
        ("DELETE", "api/providers/oauth/openai-codex"),
        ("GET", "api/credentials/pool"),
        ("DELETE", "api/credentials/pool/openai-codex/1"),
    ],
)
async def test_allowlisted_bridge_requests_preserve_scope_and_native_auth(
    monkeypatch, method, path
):
    monkeypatch.setenv("HERMES_GATEWAY_URL", "ws://native:9119/prefix/api/ws")
    monkeypatch.setenv("HERMES_SESSION_TOKEN", "native-token")
    monkeypatch.setenv("EDITH_BRIDGE_TOKEN", "bridge-token")
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://bridge",
        ) as client,
    ):
        with respx.mock:
            upstream = respx.route(method=method, url="http://native:9119/prefix/" + path).respond(
                200,
                json={
                    "ok": True,
                    "user_code": "public-code",
                    "verification_url": "https://auth.example/device",
                    "access_token": "secret-access",
                    "refresh_token": "secret-refresh",
                    "device_auth_id": "secret-id",
                    "providers": [
                        {"status": {"has_refresh_token": True, "token_preview": "secret-preview"}}
                    ],
                },
            )
            result = await client.request(
                method,
                "/dashboard/" + path,
                params={"profile": "Adam"},
                headers={"Authorization": "Bearer bridge-token"},
            )
            assert result.status_code == 200
            assert "secret-" not in result.text
            assert result.json()["user_code"] == "public-code"
            assert result.json()["providers"][0]["status"]["has_refresh_token"] is True
            request = upstream.calls[0].request
            assert request.headers["authorization"] == "Bearer native-token"
            assert request.url.params["profile"] == "Adam"


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "api/env/reveal"),
        ("POST", "api/credentials/pool"),
        ("GET", "api/providers/oauth/sessions/secret"),
        ("POST", "api/providers/oauth/openai-codex/submit"),
        ("DELETE", "api/credentials/pool/openai-codex/0"),
        ("GET", "http://evil.example/api/providers/oauth"),
    ],
)
async def test_bridge_is_not_a_general_dashboard_or_url_proxy(monkeypatch, method, path):
    monkeypatch.setenv("EDITH_BRIDGE_TOKEN", "bridge-token")
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://bridge"
    ) as client:
        result = await client.request(
            method, "/dashboard/" + path, headers={"Authorization": "Bearer bridge-token"}
        )
        assert result.status_code == 404


async def test_bridge_auth_and_query_override_rejection(monkeypatch):
    monkeypatch.setenv("EDITH_BRIDGE_TOKEN", "bridge-token")
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://bridge"
    ) as client:
        assert (await client.get("/dashboard/api/providers/oauth")).status_code == 401
        result = await client.get(
            "/dashboard/api/providers/oauth?profile=Adam&url=http://evil.example",
            headers={"Authorization": "Bearer bridge-token"},
        )
        assert result.status_code == 422


async def test_bridge_native_errors_are_sanitized(monkeypatch):
    monkeypatch.setenv("EDITH_BRIDGE_TOKEN", "bridge-token")
    monkeypatch.setenv("HERMES_GATEWAY_URL", "ws://native:9119/api/ws")
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://bridge",
        ) as client,
    ):
        with respx.mock:
            respx.get("http://native:9119/api/providers/oauth").respond(
                500, json={"detail": "secret-token-in-exception"}
            )
            result = await client.get(
                "/dashboard/api/providers/oauth?profile=Anas",
                headers={"Authorization": "Bearer bridge-token"},
            )
            assert result.status_code == 500
            assert "secret-token" not in result.text
