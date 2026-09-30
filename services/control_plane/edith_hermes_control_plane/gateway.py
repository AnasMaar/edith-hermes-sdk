"""Client for the per-pod runtime bridge."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

import httpx
import websockets

from edith_hermes_rpc import RPCPool


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
        self._rpc_pools: dict[str, RPCPool] = {}

    async def close(self) -> None:
        pools = list(self._rpc_pools.values())
        self._rpc_pools.clear()
        clients = list(self._dashboard_clients.values())
        self._dashboard_clients.clear()
        results = await asyncio.gather(
            *(pool.close() for pool in pools),
            *(client.aclose() for client in clients),
            self.client.aclose(),
            return_exceptions=True,
        )
        for result in results:
            if isinstance(result, BaseException):
                raise result

    @staticmethod
    def _connection_key(connection: dict[str, Any]) -> str:
        # Credential changes must not reuse an authenticated socket; keep the
        # credential-bearing descriptor out of the cache key's representation.
        return hashlib.sha256(json.dumps(connection, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def _dashboard_base(connection: dict[str, Any]) -> str:
        transport = next(t for t in connection["transports"] if t["kind"] == "websocket")
        parsed = urlsplit(str(transport["url"]))
        if not parsed.path.endswith("/api/ws") or parsed.scheme not in {"ws", "wss"}:
            raise ValueError("Provider authentication requires a native /api/ws transport")
        return urlunsplit(
            (
                "https" if parsed.scheme == "wss" else "http",
                parsed.netloc,
                parsed.path.removesuffix("/api/ws"),
                "",
                "",
            )
        )

    def _dashboard_client(self, connection: dict[str, Any]) -> httpx.AsyncClient:
        key = self._connection_key(connection)
        login = self._dashboard_clients.get(key)
        if login is None:
            login = httpx.AsyncClient(timeout=30)
            self._dashboard_clients[key] = login
        return login

    async def dashboard_request(
        self, connection: dict[str, Any], method: str, path: str, *, profile: str
    ) -> httpx.Response:
        """Access provider endpoints only, preserving runtime credential custody.

        HTTP transports are runtime bridges; their allowlisted /dashboard proxy
        delegates to native Hermes. WS transports use the same native dashboard
        origin and profile query, including reverse-proxy path prefixes.
        """
        if not path.startswith(("/api/providers/oauth", "/api/credentials/pool")):
            raise ValueError("Only provider authentication endpoints are allowed")
        auth = connection.get("authorization") or {}
        headers = (
            {"Authorization": "Bearer " + auth["token"]}
            if (auth.get("scheme") == "bearer" and auth.get("token"))
            else {}
        )
        transport = next((t for t in connection["transports"] if t["kind"] == "http"), None)
        if transport:
            return await self.client.request(
                method,
                transport["url"].rstrip("/") + "/dashboard" + path,
                params={"profile": profile},
                headers=headers,
            )
        base = self._dashboard_base(connection)
        if auth.get("scheme") != "dashboard_password":
            return await self.client.request(
                method, base + path, params={"profile": profile}, headers=headers
            )
        async with self._login_lock:
            login = self._dashboard_client(connection)
            response = await login.request(method, base + path, params={"profile": profile})
            if response.status_code in {401, 403, 302, 303, 307}:
                signed_in = await login.post(
                    base + "/auth/password-login",
                    json={
                        "provider": "basic",
                        "username": auth["username"],
                        "password": auth["password"],
                    },
                )
                signed_in.raise_for_status()
                response = await login.request(method, base + path, params={"profile": profile})
            return response

    async def forget(self, connection: dict[str, Any]) -> None:
        pool = self._rpc_pools.pop(self._connection_key(connection), None)
        if pool is not None:
            await pool.close()
        if (connection.get("authorization") or {}).get("scheme") == "dashboard_password":
            client = self._dashboard_clients.pop(self._connection_key(connection), None)
            if client is not None:
                await client.aclose()

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
            key = self._connection_key(connection)
            pool = self._rpc_pools.get(key)
            if pool is None:

                async def connect() -> Any:
                    return await self._connect(connection)

                pool = RPCPool(connect)
                self._rpc_pools[key] = pool
            value = await pool.request(payload, timeout=self.timeout)
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
            try:
                ready = json.loads(await asyncio.wait_for(socket.recv(), self.timeout))
                if ready.get("params", {}).get("type") != "gateway.ready":
                    raise HermesGatewayError("Bridge did not emit gateway.ready")
            except BaseException:
                with suppress(Exception):
                    await socket.close()
                raise
            return socket
        url = self._websocket_url(connection)
        authorization = connection.get("authorization") or {}
        if authorization.get("scheme") == "dashboard_password":
            parsed = urlsplit(url)
            base = self._dashboard_base(connection)
            # Separate jars by instance AND credentials: neither localhost ports
            # nor changes of authenticated identity may reuse another login.
            async with self._login_lock:
                login = self._dashboard_client(connection)
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
        try:
            first = json.loads(await asyncio.wait_for(websocket.recv(), timeout=10))
            if (
                first.get("method") != "event"
                or first.get("params", {}).get("type") != "gateway.ready"
            ):
                raise HermesGatewayError("Hermes gateway did not emit gateway.ready")
        except BaseException:
            with suppress(Exception):
                await websocket.close()
            raise
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
