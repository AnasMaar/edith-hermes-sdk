import json

import httpx
import pytest
import respx
from edith_hermes_control_plane.gateway import HermesGateway


@pytest.mark.asyncio
async def test_dashboard_login_is_reused_and_tickets_are_fresh(monkeypatch):
    urls = []

    class Socket:
        async def recv(self):
            return json.dumps({"method": "event", "params": {"type": "gateway.ready"}})

        async def close(self):
            pass

    async def connect(url, **kwargs):
        urls.append(url)
        return Socket()

    monkeypatch.setattr("edith_hermes_control_plane.gateway.websockets.connect", connect)
    gateway = HermesGateway()
    with respx.mock:
        login = respx.post("http://localhost:9119/auth/password-login").respond(
            200, json={"ok": True}, headers={"set-cookie": "session=abc; Path=/"}
        )
        respx.post("http://localhost:9119/api/auth/ws-ticket").mock(
            side_effect=[
                httpx.Response(401),
                httpx.Response(200, json={"ticket": "one"}),
                httpx.Response(200, json={"ticket": "two"}),
            ]
        )
        connection = {
            "transports": [{"kind": "websocket", "url": "ws://localhost:9119/api/ws"}],
            "authorization": {
                "scheme": "dashboard_password",
                "username": "user",
                "password": "secret",
            },
        }
        try:
            await gateway._connect(connection)
            await gateway._connect(connection)
            assert login.call_count == 1
            assert urls == [
                "ws://localhost:9119/api/ws?ticket=one",
                "ws://localhost:9119/api/ws?ticket=two",
            ]
        finally:
            await gateway.close()
