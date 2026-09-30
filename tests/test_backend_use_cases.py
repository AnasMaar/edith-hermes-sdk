"""Real HTTP/SQLite workflows against a contract-checking native gateway double.

These tests are deliberately not labelled real Hermes or real OAuth-provider tests.
"""

from __future__ import annotations

import json
from contextlib import suppress
from pathlib import Path

import httpx
import pytest
from edith_hermes_control_plane.app import create_app
from edith_hermes_control_plane.config import Settings
from edith_hermes_control_plane.gateway import HermesGatewayError

from edith_hermes import Agent, AsyncEdithHermes, External, Hermes, ToolHost
from edith_hermes.errors import RemoteError


class ContractGateway:
    def __init__(self):
        doc = json.loads(
            (
                Path(__file__).parents[1] / "contracts/vendor/hermes/gateway-contract.openrpc.json"
            ).read_text()
        )
        self.schemas = {
            m["name"]: doc["components"]["schemas"][m["params"][0]["schema"]["$ref"].split("/")[-1]]
            for m in doc["methods"]
        }
        self.calls = []
        self.count = 0
        self.cli_code = 0

    async def close(self):
        pass

    async def invoke(self, connection, method, params=None):
        params = params or {}
        schema = self.schemas[method]
        assert set(schema.get("required", [])) <= params.keys(), (method, params)
        if schema.get("additionalProperties") is False:
            assert params.keys() <= schema.get("properties", {}).keys(), (method, params)
        self.calls.append((method, params))
        result = {"ok": True}
        if method == "cli.exec":
            result = {"code": self.cli_code, "blocked": False}
        elif method in {"session.create", "session.resume", "session.branch"}:
            self.count += 1
            result = {
                "session_id": f"live-{self.count}",
                "stored_session_id": f"stored-{self.count}",
            }
        elif method == "session.events.since":
            result = {"latest_seq": 0, "epoch": "one", "events": []}
        elif method == "mcp.servers.test":
            result = {"ok": False, "oauth_needed": True, "tools": []}
        elif method == "mcp.servers.oauth.start":
            result = {
                "ok": True,
                "session_id": "oauth-flow",
                "auth_url": "https://auth.invalid/consent",
                "flow": "pkce",
            }
        elif method == "mcp.servers.oauth.poll":
            result = {"ok": True, "status": "approved", "session_id": "oauth-flow"}
        return {"jsonrpc": "2.0", "id": 1, "result": result}


@pytest.fixture
async def plane(tmp_path):
    gateway = ContractGateway()
    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'state.db'}",
        enabled_runtime_providers=["external"],
        worker_poll_seconds=0.01,
        public_base_url="http://test",
        worker_concurrency=1,
    )
    app = create_app(settings, gateway=gateway)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as http,
    ):
        sdk = AsyncEdithHermes.remote(base_url="http://test", http_client=http)
        hermes = Hermes(sdk, runtime=External("ws://test/api/ws"))
        instance = await hermes.create_instance("test", agents=[Agent("Adam"), Agent("Anas")])
        try:
            yield hermes, instance, gateway
        finally:
            from edith_hermes.errors import NotFoundError

            with suppress(NotFoundError):
                await instance.delete()
            await sdk.aclose()


@pytest.mark.parametrize("code,status", [(4008, 422), (-32602, 422), (-32603, 502)])
async def test_native_errors_preserve_actionable_details(plane, monkeypatch, code, status):
    _, instance, native = plane

    async def reject(*args, **kwargs):
        raise HermesGatewayError({"code": code, "message": "Native validation failure"})

    with monkeypatch.context() as patch:
        patch.setattr(native, "invoke", reject)
        with pytest.raises(RemoteError) as error:
            await instance.agent("Adam").sessions.create(title="rejected")
        assert error.value.status == status
        assert "Native validation failure" in str(error.value)


async def test_profile_config_and_delete_reach_native_before_registry_mutation(plane):
    _, instance, native = plane
    adam = instance.agent("Adam")
    await adam.update(soul="New instructions", config={"agent": {"max_turns": 4}})
    assert (
        "cli.exec",
        {"profile": "Adam", "argv": ["-p", "Adam", "config", "set", "agent.max_turns", "4"]},
    ) in native.calls
    assert ("profiles.configure", {"name": "Adam", "soul": "New instructions"}) in native.calls
    native.cli_code = 1
    with pytest.raises(RemoteError):
        await adam.delete()
    assert (await adam.get())["name"] == "Adam"
    native.cli_code = 0
    await adam.delete()
    assert native.calls[-1] == ("cli.exec", {"argv": ["profile", "delete", "Adam", "--yes"]})
    with pytest.raises(RemoteError) as missing:
        await adam.get()
    assert missing.value.status == 404


async def test_session_workdir_actions_resume_branch_and_delete(plane):
    _, instance, native = plane
    adam = instance.agent("Adam")
    session = await adam.sessions.create(title="task", working_directory="/tmp")
    assert native.calls[-1] == (
        "session.create",
        {"title": "task", "cwd": "/tmp", "profile": "Adam"},
    )
    handle = adam.sessions(session["id"])
    for action in ("activate", "interrupt", "close", "undo"):
        result = await handle.action(body={"type": action})
        assert result["id"] == session["id"]
        assert native.calls[-1] == (
            "session." + action,
            {"session_id": session["id"], "profile": "Adam"},
        )
    branch = await handle.action(body={"type": "branch"})
    assert branch["id"] != session["id"]
    assert (await adam.sessions(branch["id"]).get())["id"] == branch["id"]
    resumed = await handle.action(body={"type": "resume"})
    assert resumed["nativeSessionId"] != session["id"]
    assert native.calls[-1][1]["session_id"] == session["stored_session_id"]
    await handle.turns.submit(content="after resume")
    assert native.calls[-1][1]["session_id"] == resumed["nativeSessionId"]
    await handle.delete()
    assert native.calls[-1][0] == "session.delete"
    assert native.calls[-1][1]["session_id"] == resumed["stored_session_id"]


async def test_cross_profile_session_access_and_actions_are_rejected(plane):
    _, instance, native = plane
    adam, anas = instance.agent("Adam"), instance.agent("Anas")
    session = await adam.sessions.create()
    foreign = anas.sessions(session["id"])
    before = len(native.calls)
    for operation in (foreign.get(), foreign.delete(), foreign.action(body={"type": "close"})):
        with pytest.raises(RemoteError) as error:
            await operation
        assert error.value.status == 404
    assert len(native.calls) == before


async def test_prompt_modes_content_and_unsupported_overrides(plane):
    _, instance, native = plane
    adam = instance.agent("Adam")
    session = await adam.sessions.create()
    turns = adam.sessions(session["id"]).turns
    content = [{"type": "text", "text": "hello"}]
    await turns.submit(content=content, mode="steer")
    assert native.calls[-1] == (
        "prompt.submit",
        {"session_id": session["id"], "text": content, "queued": False, "profile": "Adam"},
    )
    before = len(native.calls)
    with pytest.raises(RemoteError) as failure:
        await turns.submit(content="hello", tool_binding_ids=["missing-binding"])
    assert failure.value.status == 422
    assert len(native.calls) == before
    with pytest.raises(RemoteError):
        await adam.sessions.create(environment={"KEY": "value"})


async def test_mcp_binding_filters_oauth_lifecycle_and_native_unregistration(plane):
    hermes, instance, native = plane
    adam = instance.agent("Adam")
    server = await hermes.tools.mcp_servers.create(
        name="test-server",
        transport="streamable_http",
        url="https://mcp.invalid/",
        auth="oauth",
        environment={"SAFE": "value"},
    )
    bundle = await hermes.tools.bundles.create(
        name="external", transport="mcp", mcp_server_id=server["id"]
    )
    binding = await hermes.tools.bindings.create(
        bundle_id=bundle["id"],
        scope={
            "level": "profile",
            "instanceId": instance.id,
            "profileId": adam.profile_id,
        },
    )
    registration = next(
        params for method, params in reversed(native.calls) if method == "mcp.servers.add"
    )
    assert registration == {
        "name": binding["nativeServerName"],
        "profile": "Adam",
        "config": {
            "transport": "streamable_http",
            "url": "https://mcp.invalid/",
            "auth": "oauth",
            "env": {"SAFE": "value"},
        },
    }
    session = await adam.sessions.create()
    assert native.calls[-1] == (
        "reload.mcp",
        {"session_id": session["id"], "confirm": True},
    )
    assert not (await hermes.tools.bindings.list(profile_id=instance.agent("Anas").profile_id))[
        "items"
    ]
    target = hermes.tools.mcp_servers(server["id"])
    result = await target.action(type="test")
    assert result["status"] == "needs_auth"  # Native probe, not an HTTP GET returning <500.
    started = await target.action(
        type="begin_oauth", client_redirect_uri="http://localhost:3210/callback"
    )
    assert started["result"]["auth_url"] == "https://auth.invalid/consent"
    flow = started["result"]["session_id"]
    await target.action(
        type="complete_oauth", session_id=flow, code="test-code", state="test-state"
    )
    assert native.calls[-1][0] == "mcp.servers.oauth.callback"
    assert native.calls[-1][1]["state"] == "test-state"
    assert (await target.action(type="poll_oauth", session_id=flow))["status"] == "ready"
    await target.action(type="cancel_oauth", session_id=flow)
    assert native.calls[-1][0] == "mcp.servers.oauth.cancel"
    await hermes.tools.bindings(binding["id"]).delete()
    assert (
        "mcp.servers.remove",
        {"name": binding["nativeServerName"], "profile": "Adam"},
    ) in native.calls
    assert native.calls[-1] == ("reload.mcp", {"session_id": session["id"], "confirm": True})
    with pytest.raises(RemoteError) as failure:
        await target.action(type="begin_oauth")
    assert failure.value.status == 409


def test_native_binding_names_preserve_legacy_and_room_for_tool_names():
    from edith_hermes_control_plane.engine import ProductionEngine

    binding = {"id": "binding_" + "a" * 32}
    assert ProductionEngine._binding_server_name(binding) == "edith-" + binding["id"]
    binding["nativeServerName"] = "edith-" + "a" * 20
    assert (
        len("mcp__" + ProductionEngine._binding_server_name(binding) + "__verification_multiply")
        <= 64
    )


async def test_bound_agent_open_session_validates_scope_before_selection(plane):
    _, instance, _ = plane
    adam, anas = instance.agent("Adam"), instance.agent("Anas")
    first = await adam.new_session()
    foreign = await anas.new_session()
    with pytest.raises(RemoteError) as error:
        await adam.open_session(foreign)
    assert error.value.status == 404
    assert adam.session_id == first
    second = await adam.sessions.create()
    selected = await adam.open_session(second["id"])
    assert (await selected.get())["id"] == adam.session_id == second["id"]


async def test_python_tool_lifecycle_and_lazy_session_refresh(plane):
    hermes, instance, native = plane
    hermes._host = ToolHost("https://tools.invalid")
    adam = instance.agent("Adam")

    def multiply(a: int, b: int) -> int:
        return a * b

    binding = await adam.add_tools([multiply])
    binding_id = (await binding.get())["id"]
    assert len(hermes._host.tools) == 1
    await adam.new_session()
    before = len(native.calls)
    await adam.start("Multiply")
    calls = native.calls[before:]
    assert [method for method, _ in calls] == [
        "process.list",
        "reload.mcp",
        "session.events.since",
        "prompt.submit",
    ]
    assert calls[0][1] == {"session_id": adam.session_id}
    assert calls[1][1]["confirm"] is True
    before = len(native.calls)
    await adam.start("Again")
    assert [m for m, _ in native.calls[before:]] == [
        "session.events.since",
        "prompt.submit",
    ]
    await adam.remove_tools(binding_id)
    assert not hermes._host.tools
    assert not (await hermes.tools.bundles.list())["items"]
    assert not (await hermes.tools.bindings.list())["items"]


async def test_tool_add_failure_rolls_back_callback_and_bundle(plane, monkeypatch):
    hermes, instance, native = plane
    hermes._host = ToolHost("https://tools.invalid")
    original = native.invoke

    async def fail_registration(connection, method, params=None):
        if method == "mcp.servers.add":
            raise HermesGatewayError({"code": -32603, "message": "Cannot register"})
        return await original(connection, method, params)

    monkeypatch.setattr(native, "invoke", fail_registration)

    def hello(name: str) -> str:
        return name

    with pytest.raises(RemoteError):
        await instance.agent("Adam").add_tools([hello])
    assert not hermes._host.tools
    assert not (await hermes.tools.bundles.list())["items"]
    assert not (await hermes.tools.bindings.list())["items"]


async def test_shared_tool_bundle_callback_survives_until_last_binding(plane):
    hermes, instance, _ = plane
    hermes._host = ToolHost("https://tools.invalid")
    adam, anas = instance.agent("Adam"), instance.agent("Anas")

    def hello(name: str) -> str:
        return name

    owned = await adam.add_tools([hello])
    value = await owned.get()
    shared = await hermes.tools.bindings.create(
        bundle_id=value["bundleId"],
        scope={"level": "profile", "instanceId": instance.id, "profileId": anas.profile_id},
    )
    with pytest.raises(ValueError, match="does not belong"):
        await anas.remove_tools(value["id"])
    await adam.remove_tools(value["id"])
    assert hermes._host.tools
    assert (await hermes.tools.bundles(value["bundleId"]).get())["id"] == value["bundleId"]
    await hermes.tools.bindings(shared["id"]).delete()
    await instance.delete()
    assert not hermes._host.tools
    assert not (await hermes.tools.bundles.list())["items"]


async def test_pool_leasing_concurrency_profile_and_pool_scope(plane):
    import asyncio

    hermes, _, native = plane
    pool = await hermes.pools.create(
        name="test-pool",
        desired_size=1,
        maximum_size=2,
        template={
            "runtime": {"kind": "external", "endpoint": "ws://test/api/ws"},
            "labels": {"region": "test"},
        },
    )
    handle = hermes.pools(pool["id"])
    for _ in range(100):
        ready = await handle.get()
        if ready["readySize"] == 1:
            break
        await asyncio.sleep(0.02)
    assert ready["readySize"] == 1
    claims = await asyncio.gather(
        *(
            handle.leases.acquire(ttl_seconds=60, required_labels={"region": "test"})
            for _ in range(8)
        ),
        return_exceptions=True,
    )
    successes = [claim for claim in claims if isinstance(claim, dict)]
    assert len(successes) == 1, claims
    assert all(
        isinstance(claim, dict) or isinstance(claim, RemoteError) and claim.status == 503
        for claim in claims
    )
    lease = successes[0]
    with pytest.raises(RemoteError) as wrong_pool:
        await hermes.pools("different").leases(lease["id"]).release()
    assert wrong_pool.value.status == 404
    with pytest.raises(RemoteError) as leased:
        await handle.update(desired_size=0)
    assert leased.value.status == 409
    with pytest.raises(RemoteError) as leased:
        await handle.delete()
    assert leased.value.status == 409
    await handle.leases(lease["id"]).release()
    lease = await handle.leases.acquire(
        profile={"name": "Leased", "config": {"agent.max_turns": 4}}
    )
    profile = hermes.instances(lease["instanceId"]).profiles(lease["profileId"])
    assert (await profile.get())["name"] == "Leased"
    assert (
        "cli.exec",
        {"profile": "Leased", "argv": ["-p", "Leased", "config", "set", "agent.max_turns", "4"]},
    ) in native.calls
    await handle.leases(lease["id"]).release()
    # Pool requests cannot attach another instance's profile even within one owner.
    _, instance, _ = plane
    with pytest.raises(RemoteError) as foreign_profile:
        await handle.leases.acquire(profile={"profileId": instance.agent("Adam").profile_id})
    assert foreign_profile.value.status == 404
    with pytest.raises(RemoteError) as labels:
        await handle.leases.acquire(required_labels={"region": "absent"})
    assert labels.value.status == 503
    await handle.update(desired_size=2)
    for _ in range(100):
        if (await handle.get())["readySize"] == 2:
            break
        await asyncio.sleep(0.02)
    first = await handle.leases.acquire()
    await handle.leases(first["id"]).release()
    second = await handle.leases.acquire()
    assert first["instanceId"] != second["instanceId"]
    await handle.leases(second["id"]).release()
    await handle.update(desired_size=0)
    assert (await handle.get())["currentSize"] == 0
    with pytest.raises(RemoteError) as missing:
        await profile.get()
    assert missing.value.status == 404
    await handle.delete()


@pytest.mark.parametrize(
    "options",
    [
        {"desired_size": 3, "maximum_size": 2},
        {"desired_size": -1},
        {"idle_ttl_seconds": 60},
        {"strategy": "custom"},
    ],
)
async def test_unsupported_or_invalid_pool_configuration_fails_before_creation(plane, options):
    hermes, _, _ = plane
    with pytest.raises(RemoteError) as error:
        await hermes.pools.create(
            name="invalid",
            template={"runtime": {"kind": "external", "endpoint": "ws://test/api/ws"}},
            **options,
        )
    assert error.value.status == 422
    assert not (await hermes.pools.list())["items"]


def test_allof_preserves_original_properties_and_required_fields():
    import inspect

    from edith_hermes.generated.resources import BundlesResource, McpServersResource
    from edith_hermes.models import tools

    assert {"name", "transport", "url", "auth", "environment"} <= inspect.signature(
        McpServersResource.create
    ).parameters.keys()
    assert {"name", "transport", "tools", "callback", "mcp_server_id"} <= inspect.signature(
        BundlesResource.create
    ).parameters.keys()
    assert {"name", "transport"} <= tools.CreateMcpServerRequest.__required_keys__
    assert {"name", "transport"} <= tools.CreateToolBundleRequest.__required_keys__
