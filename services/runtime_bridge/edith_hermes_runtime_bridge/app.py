"""Translate control-plane HTTP calls to Hermes' native `/api/ws` protocol."""

from __future__ import annotations

import asyncio
import json
import os
import re
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

import httpx
import websockets
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import JSONResponse, StreamingResponse

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
    application.state.dashboard_http = httpx.AsyncClient(timeout=30)
    try:
        yield
    finally:
        try:
            await application.state.rpc_pool.close()
        finally:
            await application.state.dashboard_http.aclose()


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


_PROVIDER_ROUTES = (
    ("GET", r"/api/providers/oauth"),
    ("POST", r"/api/providers/oauth/[a-zA-Z0-9_.:-]+/start"),
    ("GET", r"/api/providers/oauth/[a-zA-Z0-9_.:-]+/poll/[a-zA-Z0-9_-]+"),
    ("DELETE", r"/api/providers/oauth/sessions/[a-zA-Z0-9_-]+"),
    ("DELETE", r"/api/providers/oauth/[a-zA-Z0-9_.:-]+"),
    ("GET", r"/api/credentials/pool"),
    ("DELETE", r"/api/credentials/pool/[a-zA-Z0-9_.:-]+/[1-9][0-9]*"),
)


def _redact_auth(value: Any) -> Any:
    if isinstance(value, list):
        return [_redact_auth(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _redact_auth(item)
            for key, item in value.items()
            if key.lower()
            not in {
                "access_token",
                "refresh_token",
                "id_token",
                "api_key",
                "token",
                "token_preview",
                "device_auth_id",
                "device_code",
                "code_verifier",
                "client_secret",
            }
        }
    return value


@app.api_route("/dashboard/{path:path}", methods=["GET", "POST", "DELETE"])
async def provider_dashboard(path: str, request: Request) -> JSONResponse:
    """Allowlisted provider-auth proxy, never a general dashboard/URL proxy."""
    _authorize(request)
    route = "/" + path
    if not any(
        request.method == method and re.fullmatch(pattern, route)
        for method, pattern in _PROVIDER_ROUTES
    ):
        raise HTTPException(404, "Unsupported provider-auth route")
    if set(request.query_params) - {"profile"}:
        raise HTTPException(422, "Only the profile query parameter is supported")
    parsed = urlsplit(os.getenv("HERMES_GATEWAY_URL", "ws://127.0.0.1:9119/api/ws"))
    if parsed.scheme not in {"ws", "wss"} or not parsed.path.endswith("/api/ws"):
        raise HTTPException(501, "Unsupported native dashboard transport")
    url = urlunsplit(
        (
            "https" if parsed.scheme == "wss" else "http",
            parsed.netloc,
            parsed.path.removesuffix("/api/ws") + route,
            "",
            "",
        )
    )
    token = os.getenv("HERMES_SESSION_TOKEN", "")
    headers = {"Authorization": "Bearer " + token} if token else {}
    try:
        response = await request.app.state.dashboard_http.request(
            request.method,
            url,
            params=dict(request.query_params),
            headers=headers,
        )
        if not response.is_success:
            return JSONResponse(
                {"detail": "Native provider-auth request failed"}, status_code=response.status_code
            )
        return JSONResponse(_redact_auth(response.json()), status_code=response.status_code)
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, "Native provider-auth service unavailable") from None


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
