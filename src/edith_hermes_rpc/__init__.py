"""Internal persistent JSON-RPC transport shared by the control plane and bridge.

No command is replayed after a transport failure. Notifications remain available
through native event replay; interactive server requests require the duplex API.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4


class RPCChannel:
    def __init__(self, websocket: Any):
        self.websocket = websocket
        self.closed = False
        self.pending: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self.reader = asyncio.create_task(self._read())

    async def _read(self) -> None:
        failure: Exception = ConnectionError("Native RPC connection closed")
        try:
            async for raw in self.websocket:
                frame = json.loads(raw)
                if not isinstance(frame, dict):
                    raise ConnectionError("Invalid native JSON-RPC frame")
                if "method" in frame:
                    if "id" in frame:
                        # Never approve, reject or silently discard an interactive
                        # request on a channel that cannot expose its reply handle.
                        raise ConnectionError(
                            "Native server request requires an explicit duplex connection"
                        )
                    continue
                future = self.pending.get(str(frame.get("id")))
                if future is not None and not future.done():
                    if "result" not in frame and "error" not in frame:
                        raise ConnectionError("Native RPC response lacks result/error")
                    future.set_result(frame)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            failure = exc if isinstance(exc, ConnectionError) else ConnectionError(str(exc))
        finally:
            self.closed = True
            for future in self.pending.values():
                if not future.done():
                    future.set_exception(failure)
            await self.websocket.close()

    async def request(self, payload: dict[str, Any], *, timeout: float) -> dict[str, Any]:
        if self.closed:
            raise ConnectionError("Native RPC connection closed")
        wire_id = uuid4().hex
        future: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
        self.pending[wire_id] = future
        try:
            await self.websocket.send(json.dumps({**payload, "id": wire_id}, separators=(",", ":")))
            response = await asyncio.wait_for(future, timeout)
            return {**response, "id": payload.get("id", 1)}
        except asyncio.TimeoutError as exc:
            # Python 3.10's asyncio timeout is not the built-in TimeoutError.
            raise TimeoutError("Native RPC timed out") from exc
        finally:
            self.pending.pop(wire_id, None)
            if not future.done():
                future.cancel()
            elif not future.cancelled():
                # A simultaneous send/reader failure can leave an exception on
                # a future that the sender never got as far as awaiting.
                future.exception()

    async def close(self) -> None:
        self.closed = True
        try:
            await self.websocket.close()
        finally:
            self.reader.cancel()
            await asyncio.gather(self.reader, return_exceptions=True)


class RPCPool:
    """One retained native socket, concurrent correlated calls, explicit shutdown."""

    def __init__(self, connect: Callable[[], Awaitable[Any]]):
        self.connect = connect
        self.channel: RPCChannel | None = None
        self.lock = asyncio.Lock()
        self.closed = False

    async def request(self, payload: dict[str, Any], *, timeout: float = 300) -> dict[str, Any]:
        async with self.lock:
            if self.closed:
                raise ConnectionError("Native RPC pool closed")
            if self.channel is None or self.channel.closed:
                self.channel = RPCChannel(await self.connect())
            channel = self.channel
        # Keep the socket open after the response: native session lifetime is
        # attached to it. Never retry a command whose send may have succeeded.
        return await channel.request(payload, timeout=timeout)

    async def close(self) -> None:
        async with self.lock:
            self.closed = True
            if self.channel is not None:
                await self.channel.close()
