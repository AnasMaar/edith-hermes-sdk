"""Bounded-lifetime WebSocket relay; no automatic answers to native server requests."""

from __future__ import annotations

import asyncio
import json
from contextlib import suppress
from typing import Any

from fastapi import WebSocket

from edith_hermes.generated.operations import PROFILE_RPC_METHODS


async def relay(client: WebSocket, upstream: Any, *, profile: str | None = None) -> None:
    await client.send_json(
        {"jsonrpc": "2.0", "method": "event", "params": {"type": "gateway.ready"}}
    )

    async def send_upstream() -> None:
        while True:
            frame = await client.receive_json()
            if not isinstance(frame, dict) or frame.get("jsonrpc") != "2.0":
                await client.close(code=1008)
                return
            if profile and frame.get("method") in PROFILE_RPC_METHODS:
                params = frame.get("params") or {}
                if not isinstance(params, dict):
                    await client.close(code=1008)
                    return
                frame["params"] = {**params, "profile": profile}
            await upstream.send(json.dumps(frame))

    async def send_client() -> None:
        async for frame in upstream:
            await client.send_text(frame.decode() if isinstance(frame, bytes) else frame)

    tasks = [asyncio.create_task(send_upstream()), asyncio.create_task(send_client())]
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await upstream.close()
        with suppress(RuntimeError):
            await client.close()
