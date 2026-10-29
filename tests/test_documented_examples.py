"""Execute example functions against isolated protocol fixtures, never a live model."""

import json
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
import websockets

from edith_hermes import AsyncEdithHermes, AsyncHermesDesktop, Hermes
from edith_hermes.duplex import NativeConnection
from examples import (
    approval,
    bot_message,
    control_plane_inventory,
    desktop_schedules,
    group_attachment,
    local_tool,
    native_events,
    native_inventory,
    schedule_create,
)


async def test_control_plane_and_desktop_examples_use_scoped_reads():
    requests = []

    def handle(request):
        requests.append(request)
        if request.url.path == "/v1/instances":
            return httpx.Response(200, json={"items": []})
        if request.url.path.endswith("/sessions"):
            return httpx.Response(200, json={"items": []})
        return httpx.Response(200, json=[{"id": "job", "profile": "sandbox"}])

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="http://fixture"
    ) as http:
        async with AsyncEdithHermes.remote(base_url="http://fixture", http_client=http) as sdk:
            result = await control_plane_inventory.inspect(sdk, "i", "sandbox")
        desktop = AsyncHermesDesktop.remote(
            base_url="http://fixture", profile="sandbox", http_client=http
        )
        assert (await desktop_schedules.inspect(desktop))[0]["id"] == "job"
    assert result["sessions"] == {"items": []}
    assert [r.method for r in requests] == ["GET", "GET", "GET"]
    assert requests[1].url.path == "/v1/instances/i/profiles/sandbox/sessions"
    assert requests[2].url.params["profile"] == "sandbox"


async def test_native_inventory_and_approval_dispatch():
    calls = []

    class Driver:
        async def invoke(self, operation_id, arguments):
            calls.append((operation_id, arguments))
            return {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}

        async def aclose(self):
            pass

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return {"ok": True}

    hermes = Hermes(AsyncEdithHermes.embedded(driver=Driver()))
    profile = hermes.instances("i").profiles("sandbox")
    result = await native_inventory.inspect(profile, Connection(), "sandbox", "calendar")
    assert set(result) == {"sessions", "agents", "groups", "plugin_catalog", "connectors"}
    methods = [args["body"]["method"] for op, args in calls if op == "invokeHermesRpc"]
    assert methods == ["session.list", "agents.list", "groups.list"]
    assert calls[-2] == ("plugins.catalog.lookup", {"profile": "sandbox", "name": "calendar"})
    assert calls[-1] == ("connectors.list", {"profile": "sandbox", "owner": {"type": "account"}})
    await bot_message.send(profile, "hello sandbox")
    assert calls[-1] == (
        "invokeHermesRpc",
        {
            "instance_id": "i",
            "profile_id": "sandbox",
            "body": {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "bot_relay.deliver",
                "params": {"message": "hello sandbox"},
            },
        },
    )
    await approval.inspect_or_respond(profile, "s")
    await approval.inspect_or_respond(profile, "s", "r", "deny")
    assert calls[-1][1]["body"]["params"] == {
        "session_id": "s",
        "request_id": "r",
        "choice": "deny",
    }
    await hermes.aclose()


async def test_native_events_and_attachment_over_real_websocket(tmp_path: Path, capsys):
    frames = []

    async def server(ws):
        async for raw in ws:
            frame = json.loads(raw)
            frames.append(frame)
            method = frame["method"]
            result = {"session_id": "s"} if method == "session.create" else {"ok": True}
            if method == "session.events.since":
                result = {
                    "events": (
                        [
                            {
                                "type": "message.complete",
                                "payload": {"status": "complete", "text": "hello"},
                            }
                        ]
                        if frame["params"]["last_seen"]
                        else []
                    ),
                    "latest_seq": 1,
                    "epoch": "one",
                    "truncated": False,
                    "count": 1,
                    "open_requests": [],
                }
            if method.endswith("stage-attachment"):
                result = {"id": frame["params"]["attachment_id"]}
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": frame["id"], "result": result}))
            if method == "prompt.submit":
                await ws.send(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "method": "event",
                            "params": {"type": "message.complete", "session_id": "s"},
                        }
                    )
                )

    async with websockets.serve(server, "127.0.0.1", 0) as host:
        socket = await websockets.connect(f"ws://127.0.0.1:{host.sockets[0].getsockname()[1]}")
        connection = NativeConnection(socket, profile="sandbox")
        try:
            await native_events.run(connection, "hello", 10, 2)
            file = tmp_path / "note.txt"
            file.write_text("hello")
            await group_attachment.send(connection, "room", file, "read")
        finally:
            await connection.aclose()
    assert "turn status: completed" in capsys.readouterr().out
    assert [f["method"] for f in frames] == [
        "session.create",
        "session.events.since",
        "prompt.submit",
        "session.events.since",
        "edith.desktop.v1.groups.stage-attachment",
        "edith.desktop.v1.groups.send-attachments",
    ]
    assert frames[0]["params"] == {
        "title": "SDK example",
        "close_on_disconnect": False,
        "profile": "sandbox",
    }
    assert frames[1]["params"] == {"session_id": "s", "last_seen": 0, "profile": "sandbox"}
    assert frames[2]["params"] == {"session_id": "s", "text": "hello", "profile": "sandbox"}
    assert frames[3]["params"] == {"session_id": "s", "last_seen": 1, "profile": "sandbox"}
    assert frames[4]["params"]["room_id"] == "room"
    assert frames[4]["params"]["name"] == "note.txt"
    assert frames[4]["params"]["content_base64"] == "aGVsbG8="
    assert frames[5]["params"]["room_id"] == "room"
    assert frames[5]["params"]["payload"] == {"text": "read"}
    assert frames[5]["params"]["event_id"]
    assert frames[5]["params"]["attachment_ids"] == [frames[4]["params"]["attachment_id"]]


async def test_local_tool_example(capsys):
    await local_tool.main()
    assert json.loads(capsys.readouterr().out)["result"] == 2


async def test_schedule_timeout_reconciles_without_second_write():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith(".create"):
                raise TimeoutError("reply lost")
            return {"requestId": "request", "status": "applied", "jobId": "job"}

    receipt = await schedule_create.create(
        Connection(), "sandbox", "request", "Example", "Hello", "every 2h"
    )
    assert receipt["jobId"] == "job"
    assert [method for method, _ in calls] == [
        "edith.desktop.v1.cron.create",
        "edith.desktop.v1.cron.creation",
    ]
    assert calls[0][1] == {
        "profile": "sandbox",
        "options": {"name": "Example", "prompt": "Hello", "schedule": "every 2h", "paused": True},
        "request_id": "request",
        "timeout": 60,
    }
    assert calls[1][1]["request_id"] == "request"


@pytest.mark.parametrize("example", [native_events, group_attachment, bot_message, schedule_create])
async def test_mutating_main_requires_explicit_opt_in(example):
    # An absent --run must stop before any client or network is created.
    with pytest.raises(SystemExit, match="--run"):
        await example.main(SimpleNamespace(run=False))


async def test_approval_requires_complete_explicit_decision():
    with pytest.raises(SystemExit, match="both"):
        await approval.main(SimpleNamespace(request="request", choice=None))
    with pytest.raises(SystemExit, match="--run"):
        await approval.main(SimpleNamespace(request="request", choice="deny", run=False))


@pytest.mark.parametrize("mode", ["idle", "disconnect", "request", "other_session"])
async def test_event_stream_reports_uncertain_and_does_not_answer_requests(mode, capsys):
    import asyncio

    calls = []
    answers = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            if method == "session.create":
                return {"session_id": "ours"}
            if method == "session.events.since":
                return {"events": [], "latest_seq": 1, "epoch": "e", "truncated": False}
            return {"status": "accepted"}

        async def events(self):
            if mode == "idle":
                await asyncio.Event().wait()
            elif mode == "request":
                yield {
                    "jsonrpc": "2.0",
                    "id": "approval",
                    "method": "approval.request",
                    "params": {},
                }
            elif mode == "other_session":
                yield {
                    "jsonrpc": "2.0",
                    "method": "event",
                    "params": {"type": "message.complete", "session_id": "other"},
                }

        async def respond(self, *args, **kwargs):
            answers.append((args, kwargs))

    await native_events.run(Connection(), "hello", 1, 0.01)
    output = capsys.readouterr().out
    assert "uncertain" in output and "turn status: completed" not in output
    assert answers == []
    assert all(params.get("session_id", "ours") == "ours" for _, params in calls)
    if mode == "request":
        assert "approval.request" in output
