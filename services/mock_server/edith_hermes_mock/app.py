"""FastAPI application generated from the SDK operation catalog."""

from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

from edith_hermes.generated.operations import OPERATIONS

from .engine import MockEngine, MockProblem
from .state import SQLiteStateStore


def _token_map() -> dict[str, dict[str, str]]:
    configured = os.getenv("EDITH_MOCK_TOKENS")
    if configured:
        return json.loads(configured)
    return {
        "dev-user-1": {"tenantId": "dev", "subjectId": "user-1"},
        "dev-user-2": {"tenantId": "dev", "subjectId": "user-2"},
    }


def create_app(database: str | Path | None = None) -> FastAPI:
    database_path = database or os.getenv("EDITH_MOCK_DATABASE", "mock-state.db")
    engine = MockEngine(SQLiteStateStore(database_path))
    app = FastAPI(title="EDITH Hermes Mock Server", version="0.1.0")
    app.state.engine = engine

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"ok": True, "version": "0.1.0"}

    async def identity(request: Request) -> tuple[str, str]:
        authorization = request.headers.get("authorization", "")
        token = authorization.removeprefix("Bearer ").strip()
        value = _token_map().get(token)
        if value is None:
            raise MockProblem(401, "Unauthorized", "Supply a configured mock bearer token")
        return value["tenantId"], value["subjectId"]

    def register(operation: dict[str, Any]) -> None:
        async def endpoint(request: Request) -> Response:
            try:
                owner = await identity(request)
                try:
                    body = await request.json()
                except (json.JSONDecodeError, UnicodeDecodeError):
                    body = None
                arguments: dict[str, Any] = dict(request.path_params)
                arguments.update(request.query_params)
                if body is not None:
                    arguments["body"] = body
                if operation.get("streaming"):

                    async def events() -> AsyncIterator[str]:
                        event = {
                            "id": "event-1",
                            "type": "mock.ready",
                            "occurredAt": engine.now(),
                            "data": {"operationId": operation["operation_id"]},
                        }
                        yield f"data: {json.dumps(event)}\n\n"

                    return StreamingResponse(events(), media_type="text/event-stream")
                status, payload = await engine.handle(operation["operation_id"], arguments, owner)
                if status == 204:
                    return Response(status_code=204)
                return JSONResponse(payload, status_code=status)
            except MockProblem as problem:
                return JSONResponse(
                    problem.payload,
                    status_code=problem.status,
                    media_type="application/problem+json",
                )

        endpoint.__name__ = f"mock_{operation['python_name']}"
        app.add_api_route(
            operation["path"],
            endpoint,
            methods=[operation["method"]],
            operation_id=operation["operation_id"],
        )

    for item in OPERATIONS:
        register(item)
    return app


app = create_app()
