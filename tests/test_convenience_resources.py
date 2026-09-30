from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import get_type_hints

import httpx
import pytest

from edith_hermes import Agent, AsyncEdithHermes, BoundAgent, Hermes, Instance, ToolHost, tool
from edith_hermes.errors import RemoteError
from edith_hermes.generated import resources
from edith_hermes.generated.coverage import HTTP_COVERAGE, NATIVE_COVERAGE
from edith_hermes.generated.operations import BY_ID, HERMES_RPC_METHODS
from edith_hermes.generated.types_control_plane import CreateInstanceRequest
from edith_hermes.resources import Unset
from edith_hermes.transport import HTTPTransport


class Recorder:
    def __init__(self):
        self.calls = []
        self.reply = {"ok": True}
        self.closed = False

    async def invoke(self, operation_id, arguments):
        self.calls.append((operation_id, arguments))
        if operation_id == "invokeHermesRpc":
            return {"jsonrpc": "2.0", "id": 1, "result": self.reply}
        return self.reply

    async def stream(self, operation_id, arguments):
        self.calls.append((operation_id, arguments))
        yield {"id": "event-1", "data": {"text": "hello"}}

    async def aclose(self):
        self.closed = True


def make_hermes():
    recorder = Recorder()
    return Hermes(AsyncEdithHermes.embedded(driver=recorder)), recorder


def required_arguments(method):
    return {
        name: f"value-{name}"
        for name, param in inspect.signature(method).parameters.items()
        if param.default is inspect.Parameter.empty
    }


@pytest.mark.parametrize("operation_id", sorted(BY_ID))
async def test_every_http_operation_is_callable_and_preserves_scope(operation_id):
    hermes, recorder = make_hermes()
    class_name, method_name = HTTP_COVERAGE[operation_id].split(".")
    op = BY_ID[operation_id]
    from edith_hermes.transport import _python_name

    scope = {_python_name(k): "bound-" + k for k in op["path_parameters"] if k != "action"}
    resource = getattr(resources, class_name)(hermes.sdk, **scope)
    method = getattr(resource, method_name)
    get_type_hints(method)  # All public annotations must resolve at runtime, too.
    arguments = required_arguments(method)
    if op["streaming"]:
        assert [event async for event in method(**arguments)][0]["id"] == "event-1"
    else:
        await method(**arguments)
    called_id, wire = recorder.calls[-1]
    assert called_id == operation_id
    for key, value in scope.items():
        assert wire[key] == value
    assert not any(isinstance(v, Unset) for v in wire.values())
    assert (
        not any(isinstance(v, Unset) for v in wire.get("body", {}).values())
        if isinstance(wire.get("body"), dict)
        else True
    )
    # The existing HTTP transport must accept every generated call without leftovers.
    HTTPTransport._request_parts(op, wire)


@pytest.mark.parametrize("method_name", sorted(HERMES_RPC_METHODS))
async def test_every_native_method_has_resolvable_types_and_correct_dispatch(method_name):
    hermes, recorder = make_hermes()
    class_name, name = NATIVE_COVERAGE[method_name].split(".")
    method = getattr(
        getattr(resources, class_name)(hermes.sdk, instance_id="i", profile_id="p"), name
    )
    get_type_hints(method)
    result = await method(**required_arguments(method))
    assert result == {"ok": True}  # Unwrap JSON-RPC, without swallowing false/null results.
    op, args = recorder.calls[-1]
    assert op == "invokeHermesRpc"
    assert args["instance_id"] == "i" and args["profile_id"] == "p"
    assert args["body"]["method"] == method_name
    assert "profile" not in args["body"]["params"]


def test_coverage_exact_and_reachable_from_primary_surface():
    assert set(HTTP_COVERAGE) == set(BY_ID)
    assert set(NATIVE_COVERAGE) == set(HERMES_RPC_METHODS)
    # Traverse the actual namespace tree, not only the manifest, to catch shadowed methods.
    hermes, _ = make_hermes()
    contract = json.loads(
        (
            Path(__file__).parents[1] / "contracts/vendor/hermes/gateway-contract.openrpc.json"
        ).read_text()
    )
    from edith_hermes.transport import _python_name

    native = hermes.instances("i").profiles("p").native
    for method in contract["methods"]:
        obj = native
        parts = method["name"].split(".")
        for part in parts[:-1]:
            obj = getattr(obj, _python_name(part))
        leaf = NATIVE_COVERAGE[method["name"]].split(".")[-1]
        assert callable(getattr(obj, leaf))
    assert {"name", "runtime"} <= CreateInstanceRequest.__required_keys__


async def test_ergonomic_paths_extensions_headers_and_nulls():
    hermes, recorder = make_hermes()
    await (
        hermes.instances("i")
        .profiles("p")
        .sessions.create(title="Hello", extra_body={"future": None})
    )
    assert recorder.calls[-1] == (
        "createSession",
        {
            "instance_id": "i",
            "profile_id": "p",
            "body": {"title": "Hello", "future": None},
        },
    )
    await hermes.instances("i").update(if_match="etag", desired_state="stopped")
    path, query, body, headers = HTTPTransport._request_parts(
        BY_ID["updateInstance"], recorder.calls[-1][1]
    )
    assert headers["If-Match"] == "etag" and body == {"desiredState": "stopped"}
    await hermes.pools("pool").leases("lease").release()
    assert recorder.calls[-1][1] == {"pool_id": "pool", "lease_id": "lease"}
    await hermes.tools.bindings.list(instance_id="i", profile_id="p")
    _, query, _, _ = HTTPTransport._request_parts(BY_ID["listToolBindings"], recorder.calls[-1][1])
    assert query == {"instanceId": "i", "profileId": "p"}
    with pytest.raises(TypeError, match="Duplicate"):
        await hermes.instances("i").profiles.create(name="A", extra_body={"name": "B"})
    with pytest.raises(TypeError, match="Profile is bound"):
        await (
            hermes.instances("i")
            .profiles("p")
            .native.session.list(extra_params={"profile": "other"})
        )


async def test_existing_agent_objects_have_full_scoped_surface():
    hermes, recorder = make_hermes()
    instance = Instance(hermes, "i")
    agent = BoundAgent(instance, Agent("Adam"), "p")
    with pytest.raises(RuntimeError, match="Create a session"):
        _ = agent.session
    agent.session_id = "s"
    await agent.session.turns("t").action(body={"type": "stop"})
    assert recorder.calls[-1][1] == {
        "instance_id": "i",
        "profile_id": "p",
        "session_id": "s",
        "turn_id": "t",
        "body": {"type": "stop"},
    }
    await agent.native.approval.respond(session_id="s", request_id="r", choice="once")
    assert recorder.calls[-1][1]["body"]["params"]["choice"] == "once"


async def test_wait_timeout_does_not_cancel_and_completed_returns():
    hermes, recorder = make_hermes()
    build = hermes.images.builds("b")
    recorder.reply = {"status": "building"}
    with pytest.raises(TimeoutError, match="not cancelled"):
        await build.wait(timeout=0)
    assert all(op == "getImageBuild" for op, _ in recorder.calls)
    recorder.reply = {"status": "succeeded"}
    assert (await build.wait())["status"] == "succeeded"
    with pytest.raises(ValueError):
        await build.wait(poll_interval=0)


async def test_native_false_results_and_errors_are_not_hidden():
    hermes, recorder = make_hermes()
    recorder.reply = False
    assert await hermes.instances("i").profiles("p").native.session.list() is False

    async def fail(op, arguments):
        return {"jsonrpc": "2.0", "error": {"code": -1, "message": "failed"}}

    recorder.invoke = fail
    with pytest.raises(RemoteError):
        await hermes.instances("i").profiles("p").native.session.list()


async def test_remote_python_tool_host_and_revocation():
    @tool
    def double(value: int) -> int:
        return value * 2

    host = ToolHost("https://tools.example.test")
    url = host.register([double])
    assert url.startswith("https://tools.example.test/callbacks/")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=host.app)) as http:
        response = await http.post(
            url, json={"callId": "c", "tool": "double", "arguments": {"value": 4}}
        )
        assert response.json()["structuredContent"] == {"result": 8}
        host.unregister(url)
        assert (await http.post(url, json={})).status_code == 404
        assert (await http.get("https://tools.example.test/v1/instances")).status_code == 404


async def test_missing_tool_host_fails_before_provisioning():
    hermes, recorder = make_hermes()
    from edith_hermes import Docker

    @tool
    def hello(name: str) -> str:
        return name

    with pytest.raises(RuntimeError, match="ToolHost"):
        await hermes.create_instance(
            "test", runtime=Docker(), agents=[Agent("Adam", tools=[hello])]
        )
    assert not recorder.calls


async def test_start_handle_and_run_share_the_scoped_runtime():
    hermes, recorder = make_hermes()
    agent = BoundAgent(Instance(hermes, "i"), Agent("Adam"), "p")
    agent.session_id = "s"
    submitted = []

    async def invoke(operation, arguments):
        submitted.append((operation, arguments))
        if operation == "submitTurn":
            return {"id": "t", "status": "running"}
        if operation == "getTurn":
            return {"id": "t", "status": "completed", "output": [{"type": "text", "text": "done"}]}
        return {"accepted": True}

    recorder.invoke = invoke
    handle = await agent.start("hello", metadata={"trace": "one"}, tool_binding_ids=["b"])
    assert submitted[0][1]["body"] == {
        "content": "hello",
        "metadata": {"trace": "one"},
        "toolBindingIds": ["b"],
    }
    await handle.stop()
    assert submitted[-1][1]["body"] == {"type": "stop"}
    result = await agent.run("next")
    assert result.text == "done" and result.session_id == "s" and result.turn_id == "t"


def test_resource_generation_is_deterministic():
    import subprocess
    import sys

    root = Path(__file__).parents[1]
    files = list((root / "src/edith_hermes/generated").glob("*.py"))
    before = {path.name: path.read_bytes() for path in files}
    subprocess.run(
        [sys.executable, "scripts/generate_sdk.py"], cwd=root, check=True, capture_output=True
    )
    after = {
        path.name: path.read_bytes() for path in (root / "src/edith_hermes/generated").glob("*.py")
    }
    assert before == after
