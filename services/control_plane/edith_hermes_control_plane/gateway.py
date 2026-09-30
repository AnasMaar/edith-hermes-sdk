"""Client for the per-pod runtime bridge."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any, cast
from urllib.parse import quote, urlsplit, urlunsplit

import httpx
import websockets


class HermesGatewayError(RuntimeError):
    def __init__(self, error: dict[str, Any] | str):
        self.error = error if isinstance(error, dict) else {"message": error}
        super().__init__(str(self.error.get("message", "Native Hermes request failed")))


class HermesGateway:
    def __init__(self, timeout: float = 300):
        self.client = httpx.AsyncClient(timeout=timeout)
        self.timeout = timeout
        self._dashboard_clients: dict[str, httpx.AsyncClient] = {}
        self._login_lock = asyncio.Lock()

    async def close(self) -> None:
        for client in self._dashboard_clients.values():
            await client.aclose()
        self._dashboard_clients.clear()
        await self.client.aclose()

    async def invoke(
        self, connection: dict[str, Any], method: str, params: Any = None
    ) -> dict[str, Any]:
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        http_transport = next(
            (item for item in connection["transports"] if item["kind"] == "http"), None
        )
        if http_transport:
            auth = connection.get("authorization") or {}
            headers = (
                {"Authorization": "Bearer " + auth["token"]}
                if auth.get("scheme") == "bearer" and auth.get("token")
                else {}
            )
            response = await self.client.post(
                http_transport["url"].rstrip("/") + "/rpc", json=payload, headers=headers
            )
            response.raise_for_status()
            value: dict[str, Any] = response.json()
        else:
            websocket = await self._connect(connection)
            try:
                await websocket.send(json.dumps(payload, separators=(",", ":")))
                while True:
                    value = cast(
                        dict[str, Any],
                        json.loads(await asyncio.wait_for(websocket.recv(), self.timeout)),
                    )
                    if value.get("id") == 1 and ("result" in value or "error" in value):
                        break
            finally:
                await websocket.close()
        if value.get("error"):
            raise HermesGatewayError(value["error"])
        return value

    @staticmethod
    def _websocket_url(connection: dict[str, Any]) -> str:
        transport = next(item for item in connection["transports"] if item["kind"] == "websocket")
        url = str(transport["url"])
        authorization = connection.get("authorization") or {}
        if authorization.get("scheme") == "bearer" and authorization.get("token"):
            parsed = urlsplit(url)
            query = (
                parsed.query
                + ("&" if parsed.query else "")
                + "token="
                + quote(str(authorization["token"]), safe="")
            )
            return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))
        return url

    async def _connect(self, connection: dict[str, Any]) -> Any:
        http_transport = next((t for t in connection["transports"] if t["kind"] == "http"), None)
        if http_transport:
            base = urlsplit(http_transport["url"].rstrip("/") + "/ws")
            auth = connection.get("authorization") or {}
            headers = (
                {"Authorization": "Bearer " + auth["token"]}
                if auth.get("scheme") == "bearer"
                else {}
            )
            socket = await websockets.connect(
                urlunsplit(
                    (
                        "wss" if base.scheme == "https" else "ws",
                        base.netloc,
                        base.path,
                        base.query,
                        "",
                    )
                ),
                additional_headers=headers,
                open_timeout=self.timeout,
                max_size=16 * 1024 * 1024,
            )
            ready = json.loads(await asyncio.wait_for(socket.recv(), self.timeout))
            if ready.get("params", {}).get("type") != "gateway.ready":
                await socket.close()
                raise HermesGatewayError("Bridge did not emit gateway.ready")
            return socket
        url = self._websocket_url(connection)
        authorization = connection.get("authorization") or {}
        if authorization.get("scheme") == "dashboard_password":
            parsed = urlsplit(url)
            base = urlunsplit(
                ("https" if parsed.scheme == "wss" else "http", parsed.netloc, "", "", "")
            )
            # Separate cookie jar per instance: localhost ports share cookie domains.
            async with self._login_lock:
                login = self._dashboard_clients.get(base)
                if login is None:
                    login = httpx.AsyncClient(timeout=30)
                    self._dashboard_clients[base] = login
                response = await login.post(base + "/api/auth/ws-ticket")
                if response.status_code in {401, 403, 302, 303, 307}:
                    response = await login.post(
                        base + "/auth/password-login",
                        json={
                            "provider": "basic",
                            "username": authorization["username"],
                            "password": authorization["password"],
                        },
                    )
                    response.raise_for_status()
                    response = await login.post(base + "/api/auth/ws-ticket")
                response.raise_for_status()
                ticket = response.json()["ticket"]
            query = (
                parsed.query + ("&" if parsed.query else "") + "ticket=" + quote(ticket, safe="")
            )
            url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))
        websocket = await websockets.connect(url, open_timeout=10, max_size=16 * 1024 * 1024)
        first = json.loads(await asyncio.wait_for(websocket.recv(), timeout=10))
        if first.get("method") != "event" or first.get("params", {}).get("type") != "gateway.ready":
            await websocket.close()
            raise HermesGatewayError("Hermes gateway did not emit gateway.ready")
        return websocket

    async def events(
        self, connection: dict[str, Any], session_id: str | None
    ) -> AsyncIterator[bytes]:
        websocket = await self._connect(connection)
        try:
            if session_id:
                await websocket.send(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": "activate",
                            "method": "session.activate",
                            "params": {"session_id": session_id},
                        }
                    )
                )
            while True:
                try:
                    raw = await asyncio.wait_for(websocket.recv(), timeout=15)
                    yield f"data: {raw}\n\n".encode()
                except TimeoutError:
                    yield b": keepalive\n\n"
        finally:
            await websocket.close()
