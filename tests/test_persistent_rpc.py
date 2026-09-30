from __future__ import annotations

import asyncio
import json
from contextlib import suppress

import httpx
import pytest
import websockets
from edith_hermes_control_plane.gateway import HermesGateway, HermesGatewayError
from edith_hermes_runtime_bridge import app as bridge_module
from edith_hermes_runtime_bridge.app import app as bridge

from edith_hermes_rpc import RPCPool


def ready():
    return json.dumps({"method": "event", "params": {"type": "gateway.ready"}})


async def test_gateway_retains_session_owner_socket_and_forgets_it():
    sockets, closed = [], asyncio.Event()

    async def native(socket):
        sockets.append(socket)
        await socket.send(ready())
        active = False
        try:
            async for raw in socket:
                request = json.loads(raw)
                if request["method"] == "session.create":
                    active = True
                    result = {"session_id": "owned-session"}
                else:
                    result = {"active": active}
                await socket.send(json.dumps({"id": request["id"], "result": result}))
        finally:
            closed.set()

    async with websockets.serve(native, "127.0.0.1", 0) as server:
        connection = {
            "transports": [
                {"kind": "websocket", "url": f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}"}
            ]
        }
        gateway = HermesGateway()
        try:
            await gateway.invoke(connection, "session.create")
            # Native lifetime belongs to the socket, not the HTTP request.
            await asyncio.sleep(0.02)
            replies = await asyncio.gather(
                *(gateway.invoke(connection, "process.list") for _ in range(8))
            )
            assert all(reply["result"]["active"] for reply in replies)
            assert len(sockets) == 1
            await gateway.forget(connection)
            await asyncio.wait_for(closed.wait(), 1)
            assert not gateway._rpc_pools
        finally:
            await gateway.close()


async def test_gateway_preserves_native_error_codes_and_false_results():
    async def native(socket):
        await socket.send(ready())
        async for raw in socket:
            request = json.loads(raw)
            value = (
                {"error": {"code": 4007, "message": "session not found"}}
                if request["method"] == "missing"
                else {"result": False}
            )
            await socket.send(json.dumps({"id": request["id"], **value}))

    async with websockets.serve(native, "127.0.0.1", 0) as server:
        gateway = HermesGateway()
        connection = {
            "transports": [
                {"kind": "websocket", "url": f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}"}
            ]
        }
        try:
            with pytest.raises(HermesGatewayError) as error:
                await gateway.invoke(connection, "missing")
            assert error.value.error["code"] == 4007
            assert (await gateway.invoke(connection, "false"))["result"] is False
        finally:
            await gateway.close()


async def test_bridge_correlates_duplicate_caller_ids_out_of_order_and_drains_notifications(
    monkeypatch,
):
    sockets = []

    async def native(socket):
        sockets.append(socket)
        await socket.send(ready())
        requests = [json.loads(await socket.recv()) for _ in range(4)]
        assert len({request["id"] for request in requests}) == 4
        for index in range(300):
            await socket.send(json.dumps({"method": "event", "params": {"index": index}}))
        for request in reversed(requests):
            await socket.send(
                json.dumps({"id": request["id"], "result": request["params"]["index"]})
            )
        await socket.wait_closed()

    async with websockets.serve(native, "127.0.0.1", 0) as server:
        monkeypatch.setenv(
            "HERMES_GATEWAY_URL", f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}"
        )
        monkeypatch.delenv("HERMES_SESSION_TOKEN", raising=False)
        monkeypatch.delenv("EDITH_BRIDGE_TOKEN", raising=False)
        async with (
            bridge.router.lifespan_context(bridge),
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=bridge), base_url="http://bridge"
            ) as client,
        ):
            replies = await asyncio.gather(
                *(
                    client.post(
                        "/rpc",
                        json={
                            "jsonrpc": "2.0",
                            "id": 7,
                            "method": "read",
                            "params": {"index": index},
                        },
                    )
                    for index in range(4)
                )
            )
            assert [reply.json()["result"] for reply in replies] == list(range(4))
            assert all(reply.json()["id"] == 7 for reply in replies)
            assert len(sockets) == 1


async def test_timeout_clears_pending_call_without_replaying_or_misrouting_late_response():
    methods = []

    async def native(socket):
        first = json.loads(await socket.recv())
        methods.append(first["method"])
        await asyncio.sleep(0.05)
        await socket.send(json.dumps({"id": first["id"], "result": "late"}))
        second = json.loads(await socket.recv())
        methods.append(second["method"])
        await socket.send(json.dumps({"id": second["id"], "result": "current"}))
        await socket.wait_closed()

    async with websockets.serve(native, "127.0.0.1", 0) as server:

        async def connect():
            return await websockets.connect(f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}")

        pool = RPCPool(connect)
        try:
            with pytest.raises(TimeoutError):
                await pool.request({"id": 1, "method": "write"}, timeout=0.01)
            assert pool.channel.pending == {}
            response = await pool.request({"id": 1, "method": "read"}, timeout=1)
            assert response["result"] == "current"
            assert methods == ["write", "read"]
        finally:
            await pool.close()


async def test_reconnect_does_not_replay_an_ambiguous_write():
    methods = []

    async def native(socket):
        request = json.loads(await socket.recv())
        methods.append(request["method"])
        if request["method"] == "write":
            await socket.close()
        else:
            await socket.send(json.dumps({"id": request["id"], "result": "read"}))
            await socket.wait_closed()

    async with websockets.serve(native, "127.0.0.1", 0) as server:

        async def connect():
            return await websockets.connect(f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}")

        pool = RPCPool(connect)
        try:
            with pytest.raises(ConnectionError):
                await pool.request({"method": "write"}, timeout=1)
            assert methods == ["write"]
            assert (await pool.request({"method": "read"}, timeout=1))["result"] == "read"
            assert methods == ["write", "read"]
        finally:
            await pool.close()


async def test_interactive_server_request_is_not_automatically_answered():
    answers = []

    async def native(socket):
        await socket.recv()
        await socket.send(json.dumps({"id": "approval", "method": "approval.request"}))
        with suppress(websockets.ConnectionClosed):
            answers.append(await socket.recv())

    async with websockets.serve(native, "127.0.0.1", 0) as server:

        async def connect():
            return await websockets.connect(f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}")

        pool = RPCPool(connect)
        try:
            with pytest.raises(ConnectionError, match="duplex"):
                await pool.request({"method": "write"}, timeout=1)
            assert answers == []
        finally:
            await pool.close()


async def test_cancelled_call_keeps_other_calls_correlated_without_replay():
    received = asyncio.Event()
    methods = []

    async def native(socket):
        first = json.loads(await socket.recv())
        methods.append(first["method"])
        received.set()
        second = json.loads(await socket.recv())
        methods.append(second["method"])
        await socket.send(json.dumps({"id": first["id"], "result": "cancelled"}))
        await socket.send(json.dumps({"id": second["id"], "result": "current"}))
        await socket.wait_closed()

    async with websockets.serve(native, "127.0.0.1", 0) as server:

        async def connect():
            return await websockets.connect(f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}")

        pool = RPCPool(connect)
        try:
            task = asyncio.create_task(pool.request({"method": "write"}))
            await asyncio.wait_for(received.wait(), 1)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert pool.channel.pending == {}
            assert (await pool.request({"method": "read"}, timeout=1))["result"] == "current"
            assert methods == ["write", "read"]
        finally:
            await pool.close()


async def test_changed_bearer_credentials_never_reuse_authenticated_socket():
    connections = []

    async def native(socket):
        connections.append(socket.request.path)
        await socket.send(ready())
        async for raw in socket:
            request = json.loads(raw)
            await socket.send(json.dumps({"id": request["id"], "result": socket.request.path}))

    async with websockets.serve(native, "127.0.0.1", 0) as server:
        gateway = HermesGateway()
        base = {
            "transports": [
                {"kind": "websocket", "url": f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}"}
            ]
        }
        try:
            for token in ("first", "second", "first"):
                reply = await gateway.invoke(
                    {**base, "authorization": {"scheme": "bearer", "token": token}}, "ping"
                )
                assert reply["result"] == f"/?token={token}"
            assert connections == ["/?token=first", "/?token=second"]
            assert all("token" not in key for key in gateway._rpc_pools)
        finally:
            await gateway.close()


@pytest.mark.parametrize("target", ["control-plane", "bridge"])
@pytest.mark.parametrize("failure", ["invalid-json", "cancel"])
async def test_failed_or_cancelled_handshake_closes_socket(monkeypatch, target, failure):
    started, closed = asyncio.Event(), asyncio.Event()

    class Socket:
        async def recv(self):
            started.set()
            if failure == "cancel":
                await asyncio.Event().wait()
            return "not-json"

        async def close(self):
            closed.set()

    async def connect(*args, **kwargs):
        return Socket()

    monkeypatch.setattr(websockets, "connect", connect)
    gateway = HermesGateway()
    try:
        operation = (
            gateway._connect({"transports": [{"kind": "websocket", "url": "ws://test"}]})
            if target == "control-plane"
            else bridge_module._connect()
        )
        task = asyncio.create_task(operation)
        await asyncio.wait_for(started.wait(), 1)
        if failure == "cancel":
            task.cancel()
            expected = asyncio.CancelledError
        else:
            expected = json.JSONDecodeError
        with pytest.raises(expected):
            await task
        assert closed.is_set()
    finally:
        await gateway.close()
