import asyncio
import copy
import json

import pytest
import websockets

from edith_hermes import AsyncHermesConnectors, AsyncPluginCatalog, UnsupportedConnectorOperation
from edith_hermes.duplex import NativeConnection
from edith_hermes.errors import RemoteError

REVISION = "01K6S9SM1KKFMCM3F10XW0H0MD"


class RPC:
    def __init__(self, result=None, error=None):
        self.calls = []
        self.result = {} if result is None else result
        self.error = error

    async def call(self, method, **params):
        self.calls.append((method, params))
        if self.error:
            raise self.error
        return self.result


@pytest.mark.asyncio
async def test_account_reads_use_native_methods_and_explicit_profile():
    rpc = RPC()
    api = AsyncHermesConnectors(rpc, profile="family-edith")
    await api.list()
    await api.catalog()
    await api.tools("linear", refresh=True)
    await api.accounts()
    await api.accounts(connector="linear")
    await api.policy()
    assert rpc.calls == [
        ("connectors.list", {"profile": "family-edith", "owner": {"type": "account"}}),
        ("connectors.catalog", {"profile": "family-edith"}),
        ("connectors.tools", {"profile": "family-edith", "slug": "linear", "refresh": True}),
        ("connectors.accounts", {"profile": "family-edith"}),
        ("connectors.accounts", {"profile": "family-edith", "connector": "linear"}),
        ("connectors.policy.get", {"profile": "family-edith"}),
    ]


@pytest.mark.asyncio
async def test_connect_alias_repair_and_exact_account_identity():
    rpc = RPC()
    api = AsyncHermesConnectors(rpc, profile="door-edith")
    await api.connect(["linear"])
    await api.connect(["linear"], alias="work")
    await api.connect(["linear"], reconnect=True, connection_id="opaque-account-1")
    await api.rename_account("opaque-account-1", "personal")
    await api.remove_account("opaque-account-1")
    assert rpc.calls == [
        ("connectors.connect", dict(profile="door-edith", owner={"type": "account"}, connectors=["linear"], reconnect=False)),
        ("connectors.connect", dict(profile="door-edith", owner={"type": "account"}, connectors=["linear"], reconnect=False, alias="work")),
        ("connectors.connect", dict(profile="door-edith", owner={"type": "account"}, connectors=["linear"], reconnect=True, connection_id="opaque-account-1")),
        ("connectors.accounts.rename", dict(profile="door-edith", connection_id="opaque-account-1", alias="personal")),
        ("connectors.accounts.remove", dict(profile="door-edith", connection_id="opaque-account-1")),
    ]


@pytest.mark.asyncio
async def test_operation_owner_seq_deadline_and_unknown_fields_are_preserved():
    snapshot = {"op_id": "op-9", "seq": 8, "deadline_at": 123.5, "settled": False,
                "targets": [{"name": "linear", "kind": "connector", "action": "connect", "state": "initiated", "alias": "work"}],
                "future_backend_field": "retained"}
    rpc = RPC(snapshot)
    api = AsyncHermesConnectors(rpc, profile="door")
    owner = {"type": "session", "session_id": "actual-session-id"}
    actual = await api.connect(["linear"], owner=owner)
    assert actual is snapshot
    await api.operation_status("op-9", owner=owner)
    await api.wake_operation("op-9", owner=owner)
    await api.respond("op-9", {"targets": [{"name": "linear", "status": "skipped"}], "settled_by": "continue"}, owner=owner)
    assert rpc.calls[1] == ("connectors.operation.status", {"profile": "door", "owner": owner, "op_id": "op-9"})
    assert rpc.calls[2] == ("connectors.operation.wake", {"profile": "door", "owner": owner, "op_id": "op-9"})
    assert rpc.calls[3] == ("connection.respond", {"profile": "door", "owner": owner, "op_id": "op-9", "result": {"targets": [{"name": "linear", "status": "skipped"}], "settled_by": "continue"}})


@pytest.mark.asyncio
async def test_policy_is_a_single_checked_change_not_a_redacted_full_write():
    rpc = RPC()
    api = AsyncHermesConnectors(rpc, profile="door")
    await api.set_policy({"type": "connector", "connector": "linear", "enabled": False}, expected_revision=REVISION)
    await api.set_policy({"type": "tools", "connector": "linear", "disabled_tools": ["delete_issue"]}, expected_revision=REVISION)
    assert rpc.calls[0] == ("connectors.policy.set", {"profile": "door", "change": {"type": "connector", "connector": "linear", "enabled": False}, "expected_revision": REVISION})
    assert rpc.calls[1][1]["change"] == {"type": "tools", "connector": "linear", "disabled_tools": ["delete_issue"]}


@pytest.mark.asyncio
async def test_answer_credentials_are_sent_once_only_to_owning_backend():
    rpc = RPC()
    answer = {"targets": [{"name": "mcp", "status": "approved", "env": {"API_TOKEN": "secret-value"}}], "said": "Continue"}
    original = copy.deepcopy(answer)
    await AsyncHermesConnectors(rpc, profile="owner").respond("operation", answer)
    assert answer == original
    assert rpc.calls == [("connection.respond", {"profile": "owner", "owner": {"type": "account"}, "op_id": "operation", "result": answer})]


@pytest.mark.asyncio
async def test_unknown_capabilities_do_not_claim_support_and_use_native_error():
    failure = RemoteError(502, "Native RPC failed", body={"error": {"code": -32601}})
    rpc = RPC(error=failure)
    api = AsyncHermesConnectors(rpc, profile="owner")
    assert api.supports("connectors.accounts.rename") is None
    with pytest.raises(RemoteError) as caught:
        await api.rename_account("account-id", "work")
    assert caught.value is failure
    assert len(rpc.calls) == 1


@pytest.mark.asyncio
async def test_discovered_old_runtime_rejects_unsupported_actions_without_rpc():
    rpc = RPC()
    api = AsyncHermesConnectors(rpc, profile="owner", capabilities={
        "methods": ["connectors.connect", "connectors.list"], "named_accounts": False,
    })
    assert api.supports("connectors.connect") is True
    assert api.supports("connectors.accounts.rename") is False
    for operation in [api.rename_account("account", "work"), api.connect(["linear"], alias="work"),
                      api.connect(["linear"], reconnect=True, connection_id="account")]:
        with pytest.raises(UnsupportedConnectorOperation) as caught:
            await operation
        assert caught.value.status == 501
    assert rpc.calls == []
    await api.list()
    assert len(rpc.calls) == 1


@pytest.mark.asyncio
async def test_discovered_new_runtime_accepts_named_accounts_and_rename():
    rpc = RPC()
    api = AsyncHermesConnectors(rpc, profile="owner", capabilities={
        "methods": ["connectors.connect", "connectors.accounts.rename"], "named_accounts": True,
    })
    await api.connect(["linear"], alias="work")
    await api.rename_account("opaque-account", "home")
    assert len(rpc.calls) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [TimeoutError("uncertain"), ConnectionError("lost"), RemoteError(409, "conflict"), RemoteError(403, "not owner")])
async def test_mutation_failures_propagate_without_replay(error):
    rpc = RPC(error=error)
    with pytest.raises(type(error)) as caught:
        await AsyncHermesConnectors(rpc, profile="owner").connect(["linear"])
    assert caught.value is error
    assert len(rpc.calls) == 1


@pytest.mark.asyncio
async def test_cancellation_never_replays_or_denies_the_remote_operation():
    entered = asyncio.Event()
    calls = []

    class WaitingRPC:
        async def call(self, method, **params):
            calls.append((method, params))
            entered.set()
            await asyncio.Future()

    task = asyncio.create_task(AsyncHermesConnectors(WaitingRPC(), profile="owner").connect(["linear"]))
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(calls) == 1
    assert calls[0][0] == "connectors.connect"


@pytest.mark.parametrize("profile", ["", "all", "ALL", " other", "other "])
def test_requires_concrete_immutable_owner(profile):
    with pytest.raises(ValueError):
        AsyncHermesConnectors(RPC(), profile=profile)


def test_profile_bound_native_transport_cannot_silently_override_ownership():
    class BoundRPC(RPC):
        _profile = "family"
    with pytest.raises(ValueError, match="another profile"):
        AsyncHermesConnectors(BoundRPC(), profile="door")
    assert AsyncHermesConnectors(BoundRPC(), profile="family").profile == "family"


@pytest.mark.asyncio
@pytest.mark.parametrize("params", [
    {"connectors": []}, {"connectors": ["Linear"]},
    {"connectors": ["linear", "notion"], "alias": "work"},
    {"connectors": ["linear"], "alias": "Work"},
    {"connectors": ["linear"], "alias": "a" * 33},
    {"connectors": ["linear"], "connection_id": "id"},
    {"connectors": ["linear"], "reconnect": True, "connection_id": "id", "alias": "work"},
    {"connectors": ["linear"], "owner": {"type": "session", "session_id": ""}},
    {"connectors": ["linear"], "owner": {"type": "account", "session_id": "wrong"}},
])
async def test_invalid_connect_parameters_never_reach_backend(params):
    rpc = RPC()
    with pytest.raises(ValueError):
        await AsyncHermesConnectors(rpc, profile="owner").connect(**params)
    assert rpc.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("change,revision", [
    ({"type": "connector", "connector": "linear", "enabled": True}, "guess"),
    ({"type": "connector", "connector": "linear", "enabled": "true"}, REVISION),
    ({"type": "tools", "connector": "linear", "disabled_tools": ["a"] * 2001}, REVISION),
    ({"type": "tools", "connector": "linear", "disabled_tools": [1]}, REVISION),
    ({"type": "replace", "connectors": []}, REVISION),
    ({"type": "connector", "connector": "linear", "enabled": True, "secrets": {}}, REVISION),
])
async def test_invalid_policy_change_never_writes(change, revision):
    rpc = RPC()
    with pytest.raises(ValueError):
        await AsyncHermesConnectors(rpc, profile="owner").set_policy(change, expected_revision=revision)
    assert rpc.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("answer", [
    {"targets": [], "extra": "wrong"}, {"settled_by": "yes"}, {"said": 1},
    {"targets": {}}, {"targets": [{"name": "linear", "status": "yes"}]},
    {"targets": [{"name": "linear", "status": "approved", "env": {"TOKEN": 42}}]},
])
async def test_invalid_operation_answers_do_not_approve_anything(answer):
    rpc = RPC()
    with pytest.raises(ValueError):
        await AsyncHermesConnectors(rpc, profile="owner").respond("op", answer)
    assert rpc.calls == []


@pytest.mark.asyncio
async def test_profiles_with_duplicate_account_labels_keep_exact_scope():
    rpc = RPC()
    await AsyncHermesConnectors(rpc, profile="family").rename_account("same-id", "work")
    await AsyncHermesConnectors(rpc, profile="door").rename_account("same-id", "work")
    assert [params["profile"] for _, params in rpc.calls] == ["family", "door"]


@pytest.mark.asyncio
async def test_plugin_catalog_uses_only_existing_calls_and_preserves_status():
    result = {"status": "unavailable"}
    rpc = RPC(result)
    api = AsyncPluginCatalog(rpc, profile="family")
    assert await api.lookup("calendar") is result
    await api.presence(["calendar", "other"])
    await api.onboarding()
    assert rpc.calls == [
        ("plugins.catalog.lookup", {"profile": "family", "name": "calendar"}),
        ("plugins.manage", {"profile": "family", "action": "presence", "names": ["calendar", "other"]}),
        ("plugins.manage", {"profile": "family", "action": "onboarding"}),
    ]


@pytest.mark.asyncio
async def test_plugin_presence_action_needs_explicit_action_support_on_old_host():
    rpc = RPC()
    api = AsyncPluginCatalog(rpc, profile="family", capabilities={"methods": ["plugins.manage"], "plugin_presence": False})
    with pytest.raises(UnsupportedConnectorOperation):
        await api.presence(["calendar"])
    with pytest.raises(UnsupportedConnectorOperation):
        await api.lookup("calendar")
    assert rpc.calls == []
    await api.onboarding()
    assert len(rpc.calls) == 1


@pytest.mark.asyncio
async def test_real_duplex_transport_retains_operation_frames_profile_and_rpc_errors():
    """A real TCP/WebSocket relay with a simulated native gateway, no provider I/O."""
    frames = []
    snapshot = {"op_id": "native-op", "seq": 3, "deadline_at": 900.0,
                "settled": False, "targets": []}
    update = {**snapshot, "owner": {"type": "account"}, "from": "pending", "to": "initiated"}

    async def native(socket):
        async for raw in socket:
            frame = json.loads(raw)
            frames.append(frame)
            result = {"result": snapshot}
            if frame["method"] == "connectors.accounts.rename":
                result = {"error": {"code": -32601, "message": "unsupported on this host"}}
            await socket.send(json.dumps({"jsonrpc": "2.0", "id": frame["id"], **result}))
            if frame["method"] == "connectors.connect":
                await socket.send(json.dumps({"jsonrpc": "2.0", "method": "connection.update", "params": update}))

    async with websockets.serve(native, "127.0.0.1", 0) as server:
        socket = await websockets.connect(f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}")
        connection = NativeConnection(socket, profile="exact-profile")
        try:
            api = AsyncHermesConnectors(connection, profile="exact-profile")
            assert await api.connect(["linear"], alias="work") == snapshot
            event = await asyncio.wait_for(anext(connection.events()), 2)
            assert event == {"jsonrpc": "2.0", "method": "connection.update", "params": update}
            assert await api.operation_status("native-op") == snapshot
            with pytest.raises(RemoteError) as caught:
                await api.rename_account("immutable-native-account", "work")
            assert caught.value.body["error"]["code"] == -32601
            assert len(frames) == 3
            assert all(frame["params"]["profile"] == "exact-profile" for frame in frames)
            assert frames[0]["params"]["owner"] == {"type": "account"}
            assert frames[2]["params"]["connection_id"] == "immutable-native-account"
            assert not connection._pending
        finally:
            await connection.aclose()
