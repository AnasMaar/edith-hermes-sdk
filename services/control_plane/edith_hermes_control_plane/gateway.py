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
    pass


class HermesGateway:
    def __init__(self, timeout: float = 300):
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self.client.aclose()

    async def invoke(
        self, connection: dict[str, Any], method: str, params: Any = None
    ) -> dict[str, Any]:
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        http_transport = next(
            (item for item in connection["transports"] if item["kind"] == "http"), None
        )
        if http_transport:
            response = await self.client.post(
                http_transport["url"].rstrip("/") + "/rpc", json=payload
            )
            response.raise_for_status()
            value: dict[str, Any] = response.json()
        else:
            websocket = await self._connect(connection)
            try:
                await websocket.send(json.dumps(payload, separators=(",", ":")))
                while True:
                    value = cast(dict[str, Any], json.loads(await websocket.recv()))
                    if value.get("id") == 1 and ("result" in value or "error" in value):
                        break
            finally:
                await websocket.close()
        if value.get("error"):
            raise HermesGatewayError(str(value["error"]))
        return value

    @staticmethod
    def _websocket_url(connection: dict[str, Any]) -> str:
        transport = next(
            item for item in connection["transports"] if item["kind"] == "websocket"
        )
        url = str(transport["url"])
        authorization = connection.get("authorization") or {}
        if authorization.get("scheme") == "bearer" and authorization.get("token"):
            parsed = urlsplit(url)
            query = parsed.query + ("&" if parsed.query else "") + "token=" + quote(
                str(authorization["token"]), safe=""
            )
            return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))
        return url

    async def _connect(self, connection: dict[str, Any]) -> Any:
        websocket = await websockets.connect(
            self._websocket_url(connection), open_timeout=10, max_size=16 * 1024 * 1024
        )
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
