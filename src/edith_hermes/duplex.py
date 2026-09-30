"""Persistent JSON-RPC with notifications and explicit server-request responses."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import quote
from uuid import uuid4

from .client import AsyncEdithHermes
from .errors import RemoteError
from .generated.operations import PROFILE_RPC_METHODS
from .transport import HTTPTransport


class NativeConnection:
    def __init__(self, websocket: Any, *, profile: str | None = None, queue_size: int = 256):
        self._websocket = websocket
        self._profile = profile
        self._pending: dict[str, asyncio.Future[Any]] = {}
        self._requests: set[str | int] = set()
        self._events: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue(queue_size)
        self._failure: BaseException | None = None
        self._reader = asyncio.create_task(self._read())

    async def _read(self) -> None:
        try:
            async for raw in self._websocket:
                frame = json.loads(raw)
                if "method" not in frame and str(frame.get("id")) in self._pending:
                    future = self._pending[str(frame["id"])]
                    if not future.done():
                        if "error" in frame:
                            future.set_exception(RemoteError(502, "Native RPC failed", body=frame))
                        else:
                            future.set_result(frame.get("result"))
                else:
                    if "method" in frame and "id" in frame:
                        self._requests.add(frame["id"])
                    self._events.put_nowait(frame)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self._failure = exc
        finally:
            failure = self._failure or ConnectionError("Native connection closed")
            for future in self._pending.values():
                if not future.done():
                    future.set_exception(failure)
            # Overflow closes explicitly; never silently drops an approval request.
            if self._events.full():
                self._events.get_nowait()
            self._events.put_nowait(None)
            await self._websocket.close()

    async def call(self, method: str, *, timeout: float = 300, **params: Any) -> Any:
        if self._reader.done():
            raise ConnectionError("Native connection is closed")
        if self._profile and method in PROFILE_RPC_METHODS:
            params["profile"] = self._profile
        request_id = uuid4().hex
        future = asyncio.get_running_loop().create_future()
        self._pending[request_id] = future
        try:
            await self._websocket.send(
                json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
            )
            return await asyncio.wait_for(future, timeout)
        finally:
            self._pending.pop(request_id, None)

    async def events(self) -> AsyncIterator[dict[str, Any]]:
        """One consumer; yields both native notifications and server requests."""
        while True:
            frame = await self._events.get()
            if frame is None:
                if self._failure:
                    raise self._failure
                return
            yield frame

    async def respond(
        self, request_id: str | int, *, result: Any = None, error: dict[str, Any] | None = None
    ) -> None:
        """Answer a received server request on its originating connection."""
        if request_id not in self._requests:
            raise ValueError("Unknown or already answered server request")
        frame = {
            "jsonrpc": "2.0",
            "id": request_id,
            **({"error": error} if error is not None else {"result": result}),
        }
        await self._websocket.send(json.dumps(frame))
        self._requests.remove(request_id)

    async def aclose(self) -> None:
        await self._websocket.close()
        self._reader.cancel()
        await asyncio.gather(self._reader, return_exceptions=True)


@asynccontextmanager
async def connect(
    sdk: AsyncEdithHermes, *, instance_id: str, profile_id: str
) -> AsyncIterator[NativeConnection]:
    """HTTP clients use the scoped control-plane relay; local clients connect directly."""
    native_gateway = None
    connection = None
    try:
        if sdk._local_http is not None:
            from edith_hermes_control_plane.gateway import HermesGateway

            profile = await sdk.control_plane.get_profile(
                instance_id=instance_id, profile_id=profile_id
            )
            descriptor = await sdk.control_plane.get_instance_connection(instance_id=instance_id)
            native_gateway = HermesGateway()
            socket = await native_gateway._connect(descriptor)
            connection = NativeConnection(socket, profile=profile["name"])
        else:
            try:
                import websockets
            except ImportError as exc:
                raise RuntimeError(
                    "Install edith-hermes-sdk[streaming] for persistent WebSockets"
                ) from exc
            transport = sdk._transport
            if not isinstance(transport, HTTPTransport):
                raise RuntimeError("This embedded driver does not implement a duplex transport")
            path = f"v1/instances/{quote(instance_id, safe='')}/profiles/{quote(profile_id, safe='')}/gateway"
            url = transport._client.base_url.join(path)
            headers = {
                k: v
                for k, v in transport._client.headers.items()
                if k.lower()
                not in {
                    "connection",
                    "upgrade",
                    "host",
                    "sec-websocket-key",
                    "sec-websocket-version",
                    "sec-websocket-extensions",
                }
            }
            if transport._authorization:
                headers["Authorization"] = transport._authorization
            socket = await websockets.connect(
                str(url.copy_with(scheme="wss" if url.scheme == "https" else "ws")),
                additional_headers=headers,
                max_size=16 * 1024 * 1024,
            )
            try:
                ready = json.loads(await asyncio.wait_for(socket.recv(), 10))
                if ready.get("params", {}).get("type") != "gateway.ready":
                    raise ConnectionError("Control plane did not emit gateway.ready")
            except BaseException:
                await socket.close()
                raise
            connection = NativeConnection(socket)
        await connection.call("client.capabilities", server_requests=True)
        yield connection
    finally:
        if connection:
            await connection.aclose()
        if native_gateway:
            await native_gateway.close()
