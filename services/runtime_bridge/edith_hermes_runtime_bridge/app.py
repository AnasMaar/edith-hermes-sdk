"""Translate control-plane HTTP calls to Hermes' native `/api/ws` protocol."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator
from typing import Any, cast
from urllib.parse import quote, urlsplit, urlunsplit

import websockets
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse


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
    first = json.loads(await asyncio.wait_for(websocket.recv(), timeout=10))
    if first.get("method") != "event" or first.get("params", {}).get("type") != "gateway.ready":
        await websocket.close()
        raise RuntimeError("Hermes gateway did not emit gateway.ready")
    return websocket


app = FastAPI(title="EDITH Hermes Runtime Bridge", version="0.3.1")


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
    payload = await request.json()
    if payload.get("jsonrpc") != "2.0" or not payload.get("method"):
        raise HTTPException(422, "A JSON-RPC 2.0 method is required")
    request_id = payload.get("id", 1)
    websocket = await _connect()
    try:
        await websocket.send(json.dumps(payload, separators=(",", ":")))
        while True:
            message = json.loads(await asyncio.wait_for(websocket.recv(), timeout=300))
            if message.get("id") == request_id and ("result" in message or "error" in message):
                return cast(dict[str, Any], message)
            if "id" in message and "method" in message:
                await websocket.send(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": message["id"],
                            "error": {
                                "code": -32001,
                                "message": "Interactive response required; use the event stream",
                            },
                        }
                    )
                )
    except TimeoutError as exc:
        raise HTTPException(504, "Hermes RPC timed out") from exc
    finally:
        await websocket.close()


@app.get("/events")
async def events(request: Request) -> StreamingResponse:
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
