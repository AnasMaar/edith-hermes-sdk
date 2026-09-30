"""Production FastAPI control plane."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import JSONResponse, Response, StreamingResponse

from edith_hermes.generated.operations import OPERATIONS

from .auth import Authenticator, Identity
from .config import Settings
from .database import Database
from .duplex import relay
from .engine import Problem, ProductionEngine
from .gateway import HermesGateway, HermesGatewayError
from .providers import (
    BuildKitProvider,
    DockerProvider,
    ExternalProvider,
    KubernetesProvider,
    NousCloudProvider,
    ProcessProvider,
    RuntimeProvider,
    RuntimeRegistry,
)
from .worker import JobWorker

logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    *,
    database: Database | None = None,
    kubernetes: KubernetesProvider | None = None,
    runtimes: RuntimeRegistry | None = None,
    buildkit: BuildKitProvider | None = None,
    gateway: HermesGateway | None = None,
    start_worker: bool = True,
) -> FastAPI:
    settings = settings or Settings.from_env()
    settings.validate()
    database = database or Database(settings.database_url)
    if runtimes is None:
        if kubernetes is not None:
            # Backward-compatible injection point retained for existing integrators/tests.
            runtimes = RuntimeRegistry([kubernetes])
        else:
            providers: list[RuntimeProvider] = []
            for kind in settings.enabled_runtime_providers:
                if kind == "external":
                    providers.append(ExternalProvider())
                elif kind == "process":
                    providers.append(ProcessProvider(settings))
                elif kind == "container":
                    providers.append(DockerProvider(settings))
                elif kind == "kubernetes":
                    providers.append(KubernetesProvider(settings))
                elif kind == "nous_cloud":
                    providers.append(NousCloudProvider(settings))
            runtimes = RuntimeRegistry(providers)
    gateway = gateway or HermesGateway()
    buildkit = buildkit or BuildKitProvider(settings)
    worker = JobWorker(database, settings, buildkit, runtimes, gateway)
    engine = ProductionEngine(database, settings, runtimes, gateway)
    authenticate = Authenticator(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        await database.create_schema()
        await runtimes.start()
        if start_worker:
            worker.start()
        try:
            yield
        finally:
            if start_worker:
                await worker.stop()
            await gateway.close()
            await runtimes.close()
            await database.close()

    app = FastAPI(
        title="EDITH Hermes Production Control Plane",
        version="0.4.0",
        lifespan=lifespan,
    )
    app.state.database = database
    app.state.engine = engine
    app.state.worker = worker
    app.state.runtimes = runtimes

    @app.websocket("/v1/instances/{instance_id}/profiles/{profile_id}/gateway")
    async def native_gateway(websocket: WebSocket, instance_id: str, profile_id: str) -> None:
        try:
            identity = await authenticate.from_headers(websocket.headers)
            profile = await engine._profile_name(instance_id, profile_id, identity)
            instance = await engine._instance(instance_id, identity)
            if instance.get("status") != "ready":
                await websocket.close(code=1013)
                return
        except (HTTPException, Problem):
            await websocket.close(code=1008)
            return
        try:
            upstream = await gateway._connect(instance["connection"])
        except Exception:
            await websocket.close(code=1011)
            return
        try:
            await websocket.accept()
            await relay(websocket, upstream, profile=profile)
        finally:
            await upstream.close()

    @app.get("/health/live")
    async def live() -> dict[str, Any]:
        return {"ok": True, "version": "0.4.0"}

    @app.get("/health/ready")
    async def ready() -> dict[str, Any]:
        async with database.engine.connect() as connection:
            await connection.exec_driver_sql("SELECT 1")
        return {"ok": True, "database": True, "runtimes": runtimes.readiness()}

    async def stream_build_logs(build_id: str, identity: Identity) -> StreamingResponse:
        job = await database.get_job(build_id, identity.owner)
        if job is None or job.kind != "image_build":
            raise HTTPException(404, "Image build was not found")

        async def events() -> AsyncIterator[str]:
            offset = 0
            while True:
                current = await database.get_job(build_id, identity.owner)
                if current is None:
                    return
                lines = current.logs.splitlines()
                for index, line in enumerate(lines[offset:], start=offset):
                    yield f"id: {index}\nevent: log\ndata: {json.dumps({'line': line})}\n\n"
                offset = len(lines)
                if current.status in {"succeeded", "failed", "cancelled"}:
                    yield f"event: complete\ndata: {json.dumps({'status': current.status})}\n\n"
                    return
                import asyncio

                await asyncio.sleep(1)

        return StreamingResponse(events(), media_type="text/event-stream")

    async def stream_runtime_events(
        request: Request, arguments: dict[str, Any], identity: Identity
    ) -> StreamingResponse:
        instance = await engine.required("instance", arguments["instanceId"], identity)
        session = await engine.required("session", arguments["sessionId"], identity)
        if (
            session["instanceId"] != arguments["instanceId"]
            or session["profileId"] != arguments["profileId"]
        ):
            raise Problem(404, "Not found", "Session does not belong to this profile")
        transport = next(
            (item for item in instance["connection"]["transports"] if item["kind"] == "sse"),
            None,
        )
        native_session_id = str(session.get("nativeSessionId") or session["id"])
        query = {"sessionId": native_session_id}
        auth = instance["connection"].get("authorization") or {}
        headers = (
            {"Authorization": "Bearer " + auth["token"]}
            if auth.get("scheme") == "bearer" and auth.get("token")
            else {}
        )

        async def events() -> AsyncIterator[bytes]:
            if transport is not None:
                async with (
                    httpx.AsyncClient(timeout=None) as client,
                    client.stream(
                        "GET", transport["url"], params=query, headers=headers
                    ) as response,
                ):
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes():
                        if await request.is_disconnected():
                            return
                        yield chunk
                return
            async for chunk in gateway.events(instance["connection"], native_session_id):
                if await request.is_disconnected():
                    return
                yield chunk

        return StreamingResponse(events(), media_type="text/event-stream")

    auth_dependency = Depends(authenticate)

    def register(operation: dict[str, Any]) -> None:
        async def endpoint(request: Request, identity: Identity = auth_dependency) -> Response:
            idempotency_key: str | None = None
            idempotency_reserved = False
            try:
                body: Any = None
                if request.method not in {"GET", "DELETE"}:
                    try:
                        body = await request.json()
                    except json.JSONDecodeError:
                        body = None
                arguments: dict[str, Any] = dict(request.path_params)
                if operation["namespace"] == "providers" and (
                    set(request.query_params) - set(operation.get("query_parameters", []))
                ):
                    raise Problem(
                        422,
                        "Unsupported query parameter",
                        "Provider-auth scope is bound by the URL; query overrides are not accepted",
                    )
                arguments.update(request.query_params)
                arguments["headers"] = {
                    header: request.headers.get(header)
                    for header in operation.get("header_parameters", [])
                }
                if body is not None:
                    arguments["body"] = body
                if "Idempotency-Key" in operation.get("header_parameters", []):
                    idempotency_key = request.headers.get("idempotency-key")
                    if not idempotency_key or len(idempotency_key) < 8:
                        raise Problem(
                            400,
                            "Idempotency key required",
                            "Supply an Idempotency-Key header containing at least eight characters",
                        )
                    request_hash = hashlib.sha256(
                        json.dumps(
                            {
                                "path": dict(request.path_params),
                                "query": dict(request.query_params),
                                "body": body,
                            },
                            sort_keys=True,
                            separators=(",", ":"),
                        ).encode()
                    ).hexdigest()
                    state, saved_status, saved_response = await database.reserve_idempotency(
                        operation["operation_id"],
                        idempotency_key,
                        identity.owner,
                        request_hash,
                    )
                    if state == "conflict":
                        raise Problem(
                            409,
                            "Idempotency conflict",
                            "The key was reused for a different request",
                        )
                    if state == "in_progress":
                        raise Problem(
                            409,
                            "Request in progress",
                            "An equivalent request is still executing",
                            retryable=True,
                        )
                    if state == "complete":
                        return JSONResponse(saved_response, status_code=saved_status or 200)
                    idempotency_reserved = True
                if operation["operation_id"] == "streamImageBuildLogs":
                    return await stream_build_logs(arguments["buildId"], identity)
                if operation["operation_id"] == "streamSessionEvents":
                    return await stream_runtime_events(request, arguments, identity)
                status, payload = await engine.handle(
                    operation["operation_id"], arguments, identity
                )
                if status == 204:
                    if idempotency_key is not None and idempotency_reserved:
                        await database.complete_idempotency(
                            operation["operation_id"],
                            idempotency_key,
                            identity.owner,
                            status,
                            {},
                        )
                    return Response(status_code=204)
                if idempotency_key is not None and idempotency_reserved:
                    await database.complete_idempotency(
                        operation["operation_id"],
                        idempotency_key,
                        identity.owner,
                        status,
                        payload,
                    )
                return JSONResponse(payload, status_code=status)
            except Problem as problem:
                if idempotency_key is not None and idempotency_reserved:
                    await database.complete_idempotency(
                        operation["operation_id"],
                        idempotency_key,
                        identity.owner,
                        problem.status,
                        problem.payload,
                    )
                return JSONResponse(
                    problem.payload,
                    status_code=problem.status,
                    media_type="application/problem+json",
                )
            except HermesGatewayError as exc:
                code = exc.error.get("code")
                status = (
                    422
                    if isinstance(code, int) and (4000 <= code < 5000 or code in {-32601, -32602})
                    else 502
                )
                payload = {
                    "type": "about:blank",
                    "title": "Native Hermes rejected the request",
                    "status": status,
                    "detail": str(exc),
                    "nativeError": exc.error,
                }
                if idempotency_key is not None and idempotency_reserved:
                    await database.complete_idempotency(
                        operation["operation_id"], idempotency_key, identity.owner, status, payload
                    )
                return JSONResponse(
                    payload, status_code=status, media_type="application/problem+json"
                )
            except httpx.HTTPError as exc:
                payload = {
                    "type": "about:blank",
                    "title": "Hermes runtime unavailable",
                    "status": 502,
                    "detail": str(exc),
                    "retryable": True,
                }
                if idempotency_key is not None and idempotency_reserved:
                    await database.complete_idempotency(
                        operation["operation_id"],
                        idempotency_key,
                        identity.owner,
                        502,
                        payload,
                    )
                return JSONResponse(payload, status_code=502, media_type="application/problem+json")
            except Exception:
                logger.exception("Unhandled control-plane request failure")
                payload = {
                    "type": "about:blank",
                    "title": "Internal server error",
                    "status": 500,
                    "detail": "The request failed. Consult the control-plane trace logs.",
                    "retryable": False,
                }
                if idempotency_key is not None and idempotency_reserved:
                    await database.complete_idempotency(
                        operation["operation_id"],
                        idempotency_key,
                        identity.owner,
                        500,
                        payload,
                    )
                return JSONResponse(payload, status_code=500, media_type="application/problem+json")

        endpoint.__name__ = f"production_{operation['python_name']}"
        app.add_api_route(
            operation["path"],
            endpoint,
            methods=[operation["method"]],
            operation_id=operation["operation_id"],
        )

    for operation in OPERATIONS:
        register(operation)

    @app.post("/v1/cloud/invoke")
    async def invoke_cloud(request: Request, identity: Identity = auth_dependency) -> JSONResponse:
        del identity
        if not settings.cloud_invoke_url:
            raise HTTPException(503, "EDITH_CLOUD_INVOKE_URL is not configured")
        headers = (
            {"Authorization": f"Bearer {settings.cloud_bearer_token}"}
            if settings.cloud_bearer_token
            else {}
        )
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                settings.cloud_invoke_url,
                headers=headers,
                json=await request.json(),
            )
        if response.status_code >= 400:
            raise HTTPException(502, "Cloud management adapter rejected the request")
        return JSONResponse(response.json(), status_code=response.status_code)

    @app.post("/internal/mcp/{binding_id}")
    async def mcp_bridge(binding_id: str, request: Request) -> JSONResponse:
        found = await database.find("tool_binding", binding_id)
        if found is None:
            raise HTTPException(404, "Tool binding was not found")
        owner, binding = found
        expected = "Bearer " + binding["bridgeToken"]
        if not secrets_compare(request.headers.get("authorization", ""), expected):
            raise HTTPException(401, "Invalid tool bridge token")
        bundle = await database.get("tool_bundle", binding["bundleId"], owner)
        if bundle is None:
            raise HTTPException(410, "Tool bundle no longer exists")
        message = await request.json()
        method = message.get("method")
        request_id = message.get("id")
        if method == "initialize":
            result = {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "edith-hermes-tool-bridge", "version": "0.4.0"},
            }
        elif method == "tools/list":
            result = {
                "tools": [
                    t
                    for t in bundle.get("tools") or []
                    if binding.get("enabledTools") is None or t["name"] in binding["enabledTools"]
                ]
            }
        elif method == "tools/call":
            params = message.get("params") or {}
            tool_name = params.get("name")
            allowed = {item["name"] for item in bundle.get("tools") or []}
            if binding.get("enabledTools") is not None:
                allowed &= set(binding["enabledTools"])
            if tool_name not in allowed:
                return JSONResponse(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": "Tool is not in this binding"},
                    }
                )
            callback = bundle["callback"]
            headers: dict[str, str] = {}
            if callback.get("secretRef"):
                safe = re.sub(r"[^A-Za-z0-9_.-]", "_", callback["secretRef"])
                secret_file = Path("/var/run/secrets/edith-callback") / safe
                if not secret_file.is_file():
                    raise HTTPException(503, "Callback secret is not mounted")
                headers["Authorization"] = "Bearer " + secret_file.read_text().strip()
            callback_payload = {
                "callId": str(request_id),
                "tool": tool_name,
                "arguments": params.get("arguments") or {},
                "target": binding["scope"],
                "metadata": {"bindingId": binding_id},
            }
            async with httpx.AsyncClient(timeout=callback.get("timeoutSeconds", 60)) as client:
                response = await client.post(
                    callback["url"], json=callback_payload, headers=headers
                )
                response.raise_for_status()
                result = response.json()
                result["content"] = [
                    {"type": "text", "text": json.dumps(part.get("data"))}
                    if part.get("type") == "json"
                    else part
                    for part in result.get("content", [])
                ]
        elif method == "notifications/initialized":
            return JSONResponse({}, status_code=202)
        else:
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": "Method not found"},
                }
            )
        return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": result})

    return app


def secrets_compare(left: str, right: str) -> bool:
    import hmac

    return hmac.compare_digest(left.encode(), right.encode())
