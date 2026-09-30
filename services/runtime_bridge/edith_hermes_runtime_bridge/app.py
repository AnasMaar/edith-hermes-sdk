"""Translate control-plane HTTP calls to Hermes' native `/api/ws` protocol."""

from __future__ import annotations

import asyncio
import json
import os
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

import websockets
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import StreamingResponse

from edith_hermes_rpc import RPCPool


def _gateway_url() -> str:
    base = os.getenv("HERMES_GATEWAY_URL", "ws://127.0.0.1:9119/api/ws")
    token = os.getenv("HERMES_SESSION_TOKEN", "")
    if not token:
        return base
    parsed = urlsplit(base)
    query = parsed.query + ("&" if parsed.query else "") + "token=" + quote(token, safe="")
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))


async def _connect() -> Any:
    websocket = await websockets.connect(
        _gateway_url(),
        open_timeout=10,
        ping_interval=20,
        ping_timeout=20,
        max_size=16 * 1024 * 1024,
    )
    try:
        first = json.loads(await asyncio.wait_for(websocket.recv(), timeout=10))
        if first.get("method") != "event" or first.get("params", {}).get("type") != "gateway.ready":
            raise RuntimeError("Hermes gateway did not emit gateway.ready")
    except BaseException:
        with suppress(Exception):
            await websocket.close()
        raise
    return websocket


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    application.state.rpc_pool = RPCPool(_connect)
    try:
        yield
    finally:
        await application.state.rpc_pool.close()


app = FastAPI(title="EDITH Hermes Runtime Bridge", version="0.4.0", lifespan=lifespan)


@app.websocket("/ws")
async def duplex(client: WebSocket) -> None:
    token = os.getenv("EDITH_BRIDGE_TOKEN", "")
    if token and not secrets.compare_digest(
        client.headers.get("authorization", ""), "Bearer " + token
    ):
        await client.close(code=1008)
        return
    upstream = await _connect()
    tasks: list[asyncio.Task[None]] = []

    async def to_native() -> None:
        while True:
            await upstream.send(await client.receive_text())

    async def to_client() -> None:
        async for frame in upstream:
            await client.send_text(frame.decode() if isinstance(frame, bytes) else frame)

    try:
        await client.accept()
        await client.send_json(
            {"jsonrpc": "2.0", "method": "event", "params": {"type": "gateway.ready"}}
        )
        tasks = [asyncio.create_task(to_native()), asyncio.create_task(to_client())]
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await upstream.close()
        with suppress(RuntimeError):
            await client.close()


def _authorize(request: Request) -> None:
    token = os.getenv("EDITH_BRIDGE_TOKEN", "")
    if token and not secrets.compare_digest(
        request.headers.get("authorization", ""), "Bearer " + token
    ):
        raise HTTPException(401, "Invalid runtime bridge credential")


@app.get("/health")
async def health() -> dict[str, Any]:
    try:
        websocket = await _connect()
        await websocket.close()
    except Exception as exc:
        raise HTTPException(503, f"Hermes gateway is unavailable: {exc}") from exc
    return {"ok": True}


@app.post("/rpc")
async def rpc(request: Request) -> dict[str, Any]:
    _authorize(request)
    payload = await request.json()
    if payload.get("jsonrpc") != "2.0" or not payload.get("method"):
        raise HTTPException(422, "A JSON-RPC 2.0 method is required")
    try:
        pool: RPCPool = request.app.state.rpc_pool
        return await pool.request(payload)
    except TimeoutError as exc:
        raise HTTPException(504, "Hermes RPC timed out") from exc
    except ConnectionError as exc:
        raise HTTPException(502, str(exc)) from exc


@app.get("/events")
async def events(request: Request) -> StreamingResponse:
    _authorize(request)

    async def stream() -> AsyncIterator[str]:
        websocket = await _connect()
        try:
            session_id = request.query_params.get("sessionId")
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
            while not await request.is_disconnected():
                try:
                    raw = await asyncio.wait_for(websocket.recv(), timeout=15)
                    yield f"data: {raw}\n\n"
                except TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            await websocket.close()

    return StreamingResponse(stream(), media_type="text/event-stream")
