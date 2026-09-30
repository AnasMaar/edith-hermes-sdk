"""Real TCP/WebSocket relays with a simulated native gateway, never a real LLM."""

from __future__ import annotations

import asyncio
import json
import socket
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
import uvicorn
import websockets
from edith_hermes_control_plane.app import create_app
from edith_hermes_control_plane.config import Settings

from edith_hermes import Agent, AsyncEdithHermes, External, Hermes
from edith_hermes.duplex import NativeConnection

sys.path.insert(0, str(Path(__file__).parents[1] / "services/runtime_bridge"))
from edith_hermes_runtime_bridge.app import app as bridge_app  # noqa: E402


@asynccontextmanager
async def serve(app):
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    listener.setblocking(False)
    port = listener.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(app, log_level="error", access_log=False, ws="websockets-sansio")
    )
    task = asyncio.create_task(server.serve(sockets=[listener]))

    async def started():
        while not server.started:
            if task.done():
                await task
            await asyncio.sleep(0.01)

    try:
        await asyncio.wait_for(started(), 10)
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        await asyncio.wait_for(task, 10)
        listener.close()


@pytest.mark.parametrize("via_bridge", [False, True])
async def test_remote_duplex_auth_profile_binding_server_requests_and_disconnect(
    tmp_path, monkeypatch, via_bridge
):
    frames = []
    answer = asyncio.get_running_loop().create_future()

    async def native(ws):
        await ws.send(
            json.dumps({"jsonrpc": "2.0", "method": "event", "params": {"type": "gateway.ready"}})
        )
        async for raw in ws:
            frame = json.loads(raw)
            frames.append(frame)
            if "method" not in frame:
                if not answer.done():
                    answer.set_result(frame)
                continue
            result = {"ok": True}
            if frame["method"] == "session.create":
                result = {"session_id": "s", "stored_session_id": "stored"}
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": frame["id"], "result": result}))
            if frame["method"] == "prompt.submit":
                await ws.send(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": "request-1",
                            "method": "clarify",
                            "params": {"question": "Which option?"},
                        }
                    )
                )

    async with websockets.serve(native, "127.0.0.1", 0) as native_server:
        native_url = f"ws://127.0.0.1:{native_server.sockets[0].getsockname()[1]}/api/ws"
        monkeypatch.setenv("HERMES_GATEWAY_URL", native_url)
        monkeypatch.setenv("HERMES_SESSION_TOKEN", "")
        monkeypatch.setenv("EDITH_BRIDGE_TOKEN", "test-bridge-token")
        async with serve(bridge_app) as bridge_url:
            endpoint = bridge_url if via_bridge else native_url
            authorization = (
                {"scheme": "bearer", "token": "test-bridge-token"}
                if via_bridge
                else {"scheme": "none"}
            )
            settings = Settings(
                database_url=f"sqlite+aiosqlite:///{tmp_path / 'state.db'}",
                enabled_runtime_providers=["external"],
                auth_mode="static",
                allow_insecure_dev_auth=True,
                dev_tokens={"test-token": {"tenantId": "tenant", "subjectId": "user"}},
                worker_poll_seconds=0.01,
            )
            async with (
                serve(create_app(settings)) as base,
                Hermes.remote(
                    base,
                    token="test-token",
                    owner={"tenantId": "tenant", "subjectId": "user"},
                    runtime=External(endpoint, authorization=authorization),
                ) as hermes,
            ):
                instance = await hermes.create_instance("duplex", agents=[Agent("Adam")])
                adam = instance.agent("Adam")
                url = (
                    base.replace("http", "ws", 1)
                    + f"/v1/instances/{instance.id}/profiles/{adam.profile_id}/gateway"
                )
                with pytest.raises(websockets.exceptions.InvalidStatus):
                    async with websockets.connect(url):
                        pass
                async with adam.connect() as connection:
                    await connection.call("session.create", profile="attempted-override")
                    assert frames[-1]["params"]["profile"] == "Adam"
                    await connection.call("prompt.submit", session_id="s", text="hello")
                    events = connection.events()
                    request = await asyncio.wait_for(anext(events), 3)
                    assert request["method"] == "clarify"
                    await connection.respond(request["id"], result={"answer": "option A"})
                    assert (await asyncio.wait_for(answer, 3))["result"] == {"answer": "option A"}
                    with pytest.raises(ValueError):
                        await connection.respond("request-1", result={})
                    results = await asyncio.gather(connection.call("ping"), connection.call("ping"))
                    assert results == [{"ok": True}, {"ok": True}]
                with pytest.raises(ConnectionError):
                    await connection.call("ping")
                await instance.delete()


async def test_disconnect_fails_pending_calls():
    async def native(ws):
        await ws.recv()
        await ws.close()

    async with websockets.serve(native, "127.0.0.1", 0) as server:
        ws = await websockets.connect(f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}")
        connection = NativeConnection(ws)
        try:
            with pytest.raises(ConnectionError):
                await connection.call("ping", timeout=2)
        finally:
            await connection.aclose()


async def test_in_process_control_plane_duplex_uses_same_profile(tmp_path):
    observed = []

    async def native(ws):
        await ws.send(
            json.dumps({"jsonrpc": "2.0", "method": "event", "params": {"type": "gateway.ready"}})
        )
        async for raw in ws:
            frame = json.loads(raw)
            observed.append(frame)
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": frame["id"], "result": {"ok": True}}))

    async with websockets.serve(native, "127.0.0.1", 0) as server:
        endpoint = f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}/api/ws"
        settings = Settings(
            database_url=f"sqlite+aiosqlite:///{tmp_path / 'local.db'}",
            enabled_runtime_providers=["external"],
            worker_poll_seconds=0.01,
        )
        async with await AsyncEdithHermes.local(settings=settings) as sdk:
            hermes = Hermes(sdk, runtime=External(endpoint))
            instance = await hermes.create_instance("local", agents=[Agent("Anas")])
            try:
                async with instance.agent("Anas").connect() as connection:
                    await connection.call("session.list", profile="wrong")
                    assert observed[-1]["params"]["profile"] == "Anas"
            finally:
                await instance.delete()
