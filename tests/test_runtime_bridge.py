from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest
import websockets

sys.path.insert(0, str(Path(__file__).parents[1] / "services" / "runtime_bridge"))

from edith_hermes_runtime_bridge.app import app  # noqa: E402


@pytest.mark.asyncio
async def test_runtime_bridge_round_trips_native_json_rpc(monkeypatch: Any) -> None:
    async def handler(websocket: Any) -> None:
        await websocket.send(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "event",
                    "params": {"type": "gateway.ready", "payload": {}},
                }
            )
        )
        request = json.loads(await websocket.recv())
        await websocket.send(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "event",
                    "params": {"type": "session.changed", "payload": {}},
                }
            )
        )
        await websocket.send(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": request["id"],
                    "result": {"method": request["method"]},
                }
            )
        )

    async with websockets.serve(handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        monkeypatch.setenv("HERMES_GATEWAY_URL", f"ws://127.0.0.1:{port}/api/ws")
        monkeypatch.setenv("HERMES_SESSION_TOKEN", "test-token")
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://bridge"
        ) as client:
            response = await client.post(
                "/rpc",
                json={"jsonrpc": "2.0", "id": 7, "method": "session.list", "params": {}},
            )
        assert response.status_code == 200
        assert response.json()["result"]["method"] == "session.list"
