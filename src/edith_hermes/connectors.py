"""Profile-owned bindings for Hermes's native hosted connector RPCs.

Wire shapes follow Hermes v0.22.0 (e06df9c2eae6901f4c88f464e0ae6e753c0428b8).
These are account authentication APIs, independent of tool-execution approval.
No call is retried, including after cancellation or an uncertain mutation.
"""
from __future__ import annotations

import builtins
import re
from collections.abc import Mapping
from typing import Any, Literal, Protocol, TypedDict, cast

from typing_extensions import NotRequired

from .errors import RemoteError


class ConnectorRPC(Protocol):
    async def call(self, method: str, **params: Any) -> Any: ...


class ConnectorCapabilities(TypedDict, total=False):
    """Live discovery supplied by the owner, never inferred from a version string.

    An omitted field means unknown. ``methods`` must be the actual native RPC
    inventory; action/parameter support needs the corresponding explicit flag.
    Hermes's ``gateway.capabilities`` does not advertise this inventory.
    """

    methods: list[str]
    named_accounts: bool
    plugin_presence: bool


class AccountOwner(TypedDict):
    type: Literal["account"]


class SessionOwner(TypedDict):
    type: Literal["session"]
    session_id: str


ConnectorOwner = AccountOwner | SessionOwner
ConnectorStatus = Literal["pending", "active", "failed", "expired", "revoked", "inactive"]


class ConnectorRow(TypedDict):
    connector: str
    enabled: bool
    connected: bool
    connection_status: ConnectorStatus | None
    status_reason: str | None
    gateway_disabled_tools: list[str]


class ConnectorsList(TypedDict):
    available: bool
    connectors: list[ConnectorRow]


class ConnectorCatalogEntry(TypedDict):
    slug: str
    name: str
    description: str
    category: str
    logo_url: NotRequired[str | None]


class ConnectorCatalog(TypedDict):
    connectors: list[ConnectorCatalogEntry]


class ConnectorTool(TypedDict):
    slug: str
    name: str
    description: str
    facet: Literal["read", "write", "destructive", "unclassified"]
    hints: list[str]
    categories: list[str]
    no_auth: bool
    deprecated: bool


class ConnectorTools(TypedDict):
    connector: str
    toolkit_version: str
    etag: str
    fetched_at: float
    source: Literal["cache", "network", "revalidated"]
    stale: bool
    tools: list[ConnectorTool]


class ConnectorAccount(TypedDict):
    connection_id: str
    connector: str
    status: ConnectorStatus
    label: str
    active: bool
    created_at: str
    updated_at: str
    status_reason: NotRequired[str | None]
    alias: NotRequired[str | None]
    disabled: NotRequired[bool]


class ConnectorAccounts(TypedDict):
    accounts: list[ConnectorAccount]


class ConnectorAccountRemoval(TypedDict):
    connection_id: str
    connector: str
    status: Literal["removed"]


class ConnectorPolicyTags(TypedDict, total=False):
    enable: list[str] | None
    disable: list[str] | None


class ConnectorUnrestrictedPolicy(TypedDict):
    mode: Literal["unrestricted"]


class ConnectorDenyAllPolicy(TypedDict):
    mode: Literal["deny-all"]


class ConnectorAllowPolicy(TypedDict):
    mode: Literal["allow"]
    connectors: list[str]
    tools: dict[str, list[str]]
    tags: NotRequired[ConnectorPolicyTags | None]


class ConnectorDenyPolicy(TypedDict):
    mode: Literal["deny"]
    disabled_connectors: list[str]
    tools: dict[str, list[str]]
    tags: NotRequired[ConnectorPolicyTags | None]


ConnectorPolicyBody = (
    ConnectorUnrestrictedPolicy | ConnectorDenyAllPolicy | ConnectorAllowPolicy | ConnectorDenyPolicy
)


class EffectivePolicyMetadata(TypedDict):
    version: Literal[1]
    revision: str
    issued_at_ms: int


class EffectiveUnrestrictedPolicy(ConnectorUnrestrictedPolicy, EffectivePolicyMetadata):
    pass


class EffectiveDenyAllPolicy(ConnectorDenyAllPolicy, EffectivePolicyMetadata):
    pass


class EffectiveAllowPolicy(ConnectorAllowPolicy, EffectivePolicyMetadata):
    pass


class EffectiveDenyPolicy(ConnectorDenyPolicy, EffectivePolicyMetadata):
    pass


EffectiveConnectorPolicy = (
    EffectiveUnrestrictedPolicy | EffectiveDenyAllPolicy | EffectiveAllowPolicy | EffectiveDenyPolicy
)


class ConnectorPolicyLayer(TypedDict):
    kind: Literal["org", "role", "member"]
    revision: str
    body: ConnectorPolicyBody


class ConnectorPolicy(TypedDict):
    layers: list[ConnectorPolicyLayer]
    effective: EffectiveConnectorPolicy


class ConnectorEnabledChange(TypedDict):
    type: Literal["connector"]
    connector: str
    enabled: bool


class ConnectorToolsChange(TypedDict):
    type: Literal["tools"]
    connector: str
    disabled_tools: list[str]


ConnectorPolicyChange = ConnectorEnabledChange | ConnectorToolsChange


class ConnectorPolicyUpdate(TypedDict):
    revision: str
    effective: EffectiveConnectorPolicy


class ConnectionEnvironmentField(TypedDict):
    name: str
    required: bool
    secret: bool
    default: str
    prompt: NotRequired[str | None]


class CatalogScan(TypedDict):
    status: Literal["passed", "warnings", "failed"]
    summary: str


class CatalogApproved(TypedDict):
    force: bool
    enable: bool
    ref: NotRequired[str | None]


class CatalogServerError(TypedDict):
    name: str
    error: str


ConnectionState = Literal[
    "pending", "initiated", "connected", "skipped", "failed", "expired", "not_connected"
]
ConnectionSettleReason = Literal["all_resolved", "continue", "deadline", "interrupt"]
CatalogAppState = Literal["present", "missing_app", "app_not_running", "unknown"]


class ConnectionTarget(TypedDict):
    name: str
    kind: Literal["connector", "mcp", "plugin", "skill"]
    action: Literal["authorize", "connect", "enable", "install", "reconnect"]
    state: ConnectionState
    resolved: NotRequired[bool | None]
    detail: NotRequired[str | None]
    instructions: NotRequired[str | None]
    discovery_error: NotRequired[str | None]
    connect_url: NotRequired[str | None]
    connection_id: NotRequired[str | None]
    alias: NotRequired[str | None]
    attempt: NotRequired[str | None]
    required_env: NotRequired[list[ConnectionEnvironmentField] | None]
    tools: NotRequired[list[str] | None]
    hint: NotRequired[str | None]
    display: NotRequired[str | None]
    description: NotRequired[str | None]
    tier: NotRequired[Literal["official", "community"] | None]
    platforms: NotRequired[list[str] | None]
    repo: NotRequired[str | None]
    sha: NotRequired[str | None]
    subdir: NotRequired[str | None]
    scan: NotRequired[CatalogScan | None]
    requires_hermes: NotRequired[str | None]
    has_desktop_half: NotRequired[bool | None]
    target_profile: NotRequired[str | None]
    app_state: NotRequired[CatalogAppState | None]
    skill: NotRequired[str | None]
    phase: NotRequired[Literal["downloading", "python_packages", "loading_tools"] | None]
    approved: NotRequired[CatalogApproved | None]
    enabled: NotRequired[bool | None]
    missing_env: NotRequired[list[str] | None]
    server_errors: NotRequired[list[CatalogServerError] | None]
    already_installed: NotRequired[bool | None]


class ConnectionOperation(TypedDict):
    op_id: str
    seq: int
    deadline_at: float
    settled: bool
    targets: list[ConnectionTarget]
    settled_at: NotRequired[float | None]
    settled_by: NotRequired[ConnectionSettleReason | None]
    status: NotRequired[Literal["initiated", "settled"] | None]
    note: NotRequired[str | None]


class ConnectionDisplay(TypedDict):
    suggested: list[str]


class ConnectionRequest(TypedDict):
    op_id: str
    seq: int
    deadline_at: float
    timeout_seconds: float
    targets: list[ConnectionTarget]
    tool_call_id: NotRequired[str | None]
    display: NotRequired[ConnectionDisplay | None]


# ``from`` is reserved in Python; retain the exact native key in event types.
ConnectionUpdateFrame = TypedDict(
    "ConnectionUpdateFrame", {"from": NotRequired[ConnectionState | None]}, total=False
)


class ConnectionUpdate(ConnectionOperation, ConnectionUpdateFrame):
    owner: ConnectorOwner
    target: NotRequired[str | None]
    to: NotRequired[ConnectionState | None]
    actor: NotRequired[Literal["user", "backend_watcher", "clock"] | None]
    detail: NotRequired[str | None]


class ConnectionAnswerTarget(TypedDict):
    name: str
    status: Literal["approved", "skipped"]
    detail: NotRequired[str | None]
    env: NotRequired[dict[str, str] | None]


class ConnectionAnswer(TypedDict, total=False):
    targets: list[ConnectionAnswerTarget]
    settled_by: ConnectionSettleReason | None
    said: str | None


class ConnectionAnswerReceipt(TypedDict):
    status: Literal["ok"]
    settled: bool


class ConnectionWakeReceipt(TypedDict):
    status: Literal["ok"]


class UnsupportedConnectorOperation(RemoteError):
    """The owner's live capability inventory explicitly excludes an operation."""

    def __init__(self, method: str):
        self.method = method
        super().__init__(501, "Unsupported connector operation", detail=method)


def _identity(value: str, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"Choose a nonempty {label}")
    return value


def _owner(value: ConnectorOwner | None) -> ConnectorOwner:
    if value is None:
        return {"type": "account"}
    if value == {"type": "account"}:
        return {"type": "account"}
    if value.get("type") == "session" and set(value) == {"type", "session_id"}:
        return {"type": "session", "session_id": _identity(cast(SessionOwner, value)["session_id"], "session ID")}
    raise ValueError("A connector owner is an account or an exact session ID")


class _ScopedNativeRPC:
    def __init__(self, rpc: ConnectorRPC, *, profile: str,
                 capabilities: ConnectorCapabilities | None = None):
        self.profile = _identity(profile, "owning profile")
        if self.profile.lower() == "all":
            raise ValueError("Connector operations require a concrete owning profile")
        bound_profile = getattr(rpc, "_profile", None)
        if isinstance(bound_profile, str) and bound_profile != profile:
            raise ValueError("The RPC connection belongs to another profile")
        self.rpc = rpc
        self._methods = frozenset(capabilities["methods"]) if capabilities is not None and "methods" in capabilities else None
        self._capabilities = dict(capabilities or {})

    def supports(self, method: str) -> bool | None:
        """``None`` means undiscovered; it must not be advertised as supported."""
        return method in self._methods if self._methods is not None else None

    def _require(self, method: str, feature: str | None = None) -> None:
        if self.supports(method) is False or (feature and self._capabilities.get(feature) is False):
            raise UnsupportedConnectorOperation(method)

    async def _call(self, method: str, **params: Any) -> Any:
        self._require(method)
        return await self.rpc.call(method, profile=self.profile, **params)


class AsyncHermesConnectors(_ScopedNativeRPC):
    """Native hosted accounts, policies and authorization operations for one profile.

    Persist operation references with the profile AND owner that opened them.
    ``op_id`` is not a session ID, and a hosted account's ``connection_id`` is not
    an EDITH transport connection ID. Responses keep native snapshots and seq.
    """

    async def list(self, *, owner: ConnectorOwner | None = None) -> ConnectorsList:
        return cast(ConnectorsList, await self._call("connectors.list", owner=_owner(owner)))

    async def catalog(self) -> ConnectorCatalog:
        return cast(ConnectorCatalog, await self._call("connectors.catalog"))

    async def tools(self, slug: str, *, refresh: bool = False) -> ConnectorTools:
        return cast(ConnectorTools, await self._call("connectors.tools", slug=_identity(slug, "connector slug"), refresh=refresh))

    async def connect(self, connectors: builtins.list[str], *, owner: ConnectorOwner | None = None,
                      reconnect: bool = False, alias: str | None = None,
                      connection_id: str | None = None) -> ConnectionOperation:
        if not connectors or any(not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", slug) for slug in connectors):
            raise ValueError("Choose at least one valid connector slug")
        params: dict[str, Any] = {"owner": _owner(owner), "connectors": list(connectors), "reconnect": reconnect}
        if alias is not None:
            self._require("connectors.connect", "named_accounts")
            if len(connectors) != 1 or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,31}", alias):
                raise ValueError("An alias names exactly one connector and contains 1-32 lowercase letters, digits or hyphens")
            params["alias"] = alias
        if connection_id is not None:
            self._require("connectors.connect", "named_accounts")
            if not reconnect or len(connectors) != 1 or alias is not None:
                raise ValueError("Repairing an account requires reconnect, one connector and no alias")
            params["connection_id"] = _identity(connection_id, "hosted account ID")
        return cast(ConnectionOperation, await self._call("connectors.connect", **params))

    async def accounts(self, *, connector: str | None = None) -> ConnectorAccounts:
        params = {} if connector is None else {"connector": _identity(connector, "connector slug")}
        return cast(ConnectorAccounts, await self._call("connectors.accounts", **params))

    async def rename_account(self, connection_id: str, alias: str) -> ConnectorAccount:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,31}", alias):
            raise ValueError("Use a 1-32 character lowercase hosted account alias")
        return cast(ConnectorAccount, await self._call("connectors.accounts.rename", connection_id=_identity(connection_id, "hosted account ID"), alias=alias))

    async def remove_account(self, connection_id: str) -> ConnectorAccountRemoval:
        return cast(ConnectorAccountRemoval, await self._call("connectors.accounts.remove", connection_id=_identity(connection_id, "hosted account ID")))

    async def policy(self) -> ConnectorPolicy:
        return cast(ConnectorPolicy, await self._call("connectors.policy.get"))

    async def set_policy(self, change: ConnectorPolicyChange, *, expected_revision: str) -> ConnectorPolicyUpdate:
        if not re.fullmatch(r"[0-7][0-9A-HJKMNP-TV-Z]{25}", expected_revision):
            raise ValueError("Use the exact native policy revision returned by the backend")
        if change.get("type") == "connector":
            valid = set(change) == {"type", "connector", "enabled"} and isinstance(change.get("enabled"), bool)
        elif change.get("type") == "tools":
            disabled = change.get("disabled_tools")
            valid = set(change) == {"type", "connector", "disabled_tools"} and isinstance(disabled, list) and len(disabled) <= 2000 and all(isinstance(item, str) for item in disabled)
        else:
            valid = False
        if not valid:
            raise ValueError("Use one native connector or disabled-tools policy change")
        _identity(change["connector"], "connector slug")
        return cast(ConnectorPolicyUpdate, await self._call("connectors.policy.set", change=dict(change), expected_revision=expected_revision))

    async def operation_status(self, op_id: str, *, owner: ConnectorOwner | None = None) -> ConnectionOperation:
        return cast(ConnectionOperation, await self._call("connectors.operation.status", owner=_owner(owner), op_id=_identity(op_id, "operation ID")))

    async def wake_operation(self, op_id: str, *, owner: ConnectorOwner | None = None) -> ConnectionWakeReceipt:
        """Read accounts promptly after the browser returns; this is not connect retry."""
        return cast(ConnectionWakeReceipt, await self._call("connectors.operation.wake", owner=_owner(owner), op_id=_identity(op_id, "operation ID")))

    async def respond(self, op_id: str, result: ConnectionAnswer, *, owner: ConnectorOwner | None = None) -> ConnectionAnswerReceipt:
        """Answer the owning operation; credential fields go directly to its backend.

        This does not approve an agent tool call. Cancelling this coroutine only
        stops waiting: reconcile operation_status before any further action.
        """
        if set(result) - {"targets", "settled_by", "said"}:
            raise ValueError("Unknown connection answer fields")
        if result.get("settled_by") not in {None, "all_resolved", "continue", "deadline", "interrupt"}:
            raise ValueError("Unknown connection settlement reason")
        if result.get("said") is not None and not isinstance(result["said"], str):
            raise ValueError("The display answer must be text")
        targets = result.get("targets", [])
        if not isinstance(targets, list):
            raise ValueError("Connection answers require a target list")
        for target in targets:
            if not isinstance(target, Mapping) or set(target) - {"name", "status", "detail", "env"}:
                raise ValueError("Invalid connection target answer")
            _identity(target.get("name"), "target name")
            if target.get("status") not in {"approved", "skipped"}:
                raise ValueError("A target answer must be approved or skipped")
            env = target.get("env")
            if env is not None and (not isinstance(env, Mapping) or not all(isinstance(k, str) and isinstance(v, str) for k, v in env.items())):
                raise ValueError("Credential answers require string keys and values")
        return cast(ConnectionAnswerReceipt, await self._call("connection.respond", owner=_owner(owner), op_id=_identity(op_id, "operation ID"), result=dict(result)))
