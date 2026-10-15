# Hosted connectors and the curated plugin catalog

SDK 0.34 adds `AsyncHermesConnectors` and `AsyncPluginCatalog` around Hermes's
existing RPC transport. They use the owner/account contracts from Hermes
v0.22.0, commit `e06df9c2eae6901f4c88f464e0ae6e753c0428b8`.
The [source manifest](../contracts/vendor/hermes/hosted-connectors.sources.json)
records the exact source files and hashes inspected for these bindings.

```python
from edith_hermes import AsyncHermesConnectors, AsyncPluginCatalog

# rpc is the existing authenticated native connection for this exact profile.
connectors = AsyncHermesConnectors(rpc, profile="family-edith")
catalog = await connectors.catalog()
accounts = await connectors.accounts(connector="linear")
tools = await connectors.tools("linear")

# The backend owns browser authentication and its operation deadline.
operation = await connectors.connect(["linear"], alias="work")
snapshot = await connectors.operation_status(operation["op_id"])

plugins = AsyncPluginCatalog(rpc, profile="family-edith")
pin = await plugins.lookup("catalog-plugin-name")
# Review/install remains a separate consent-bearing administration operation.
```

Use `models.connectors` and `models.plugin_catalog`, or their public modules,
for the wire-shape TypedDicts. Results retain native keys and unknown future
fields, as the other SDK bindings do; they are not runtime-validated models.

## Operations and ownership

| SDK call | Native RPC / action |
| --- | --- |
| `list(owner=...)` | `connectors.list` |
| `catalog()` | `connectors.catalog` |
| `tools(slug, refresh=False)` | `connectors.tools` |
| `accounts(connector=None)` | `connectors.accounts` |
| `connect(connectors, owner=..., reconnect=False, alias=None, connection_id=None)` | `connectors.connect` |
| `rename_account(connection_id, alias)` | `connectors.accounts.rename` |
| `remove_account(connection_id)` | `connectors.accounts.remove` |
| `policy()` | `connectors.policy.get` |
| `set_policy(change, expected_revision=...)` | `connectors.policy.set` |
| `operation_status(op_id, owner=...)` | `connectors.operation.status` |
| `wake_operation(op_id, owner=...)` | `connectors.operation.wake` |
| `respond(op_id, result, owner=...)` | `connection.respond` |
| `AsyncPluginCatalog.lookup(name)` | `plugins.catalog.lookup` |
| `AsyncPluginCatalog.presence(names)` | `plugins.manage`, action `presence` |
| `AsyncPluginCatalog.onboarding()` | `plugins.manage`, action `onboarding` |

Every call explicitly includes the concrete owning profile. An RPC connection
already bound to another profile is rejected. The owner defaults to
`{"type": "account"}`; session operations require
`{"type": "session", "session_id": "exact-session-id"}`. Persist the profile,
owner and `op_id` together and restore the same scope when reconciling. Accounts
route by opaque `connection_id`, never by alias or display label. A hosted
`connection_id` is separate from the application's Hermes transport connection.

The SDK preserves full operation snapshots, `seq`, deadline and target states.
An application should ignore old or duplicate frames based on the native `seq`;
the SDK does not derive optimistic authorization state. `connection.request`
and `connection.update` frames remain available on the existing duplex event
stream, with shapes `ConnectionRequest` and `ConnectionUpdate`.

`connect(alias=...)` names exactly one connector account. Repairing an opaque
account requires one connector, `reconnect=True`, `connection_id=...` and no
alias. Retired/disabled accounts remain represented by the backend's `disabled`
flag and must not be presented as selectable accounts.

Policy changes are one native connector/tool delta with the exact returned
revision. A conflict propagates without replacing the whole policy or retrying.
Connection answers may carry the exact credential fields requested by a native
MCP operation; send these only to that operation's owning backend. Neither the
SDK nor the application should log them. Account authentication and these
connection answers do not authorize an agent's tool execution.

## Discovery and compatibility

Pass a `ConnectorCapabilities` snapshot from the owning live deployment when
available:

```python
capabilities = {
    "methods": actual_native_method_names,
    "named_accounts": actual_named_account_parameter_support,
    "plugin_presence": actual_presence_action_support,
}
connectors = AsyncHermesConnectors(rpc, profile="family-edith", capabilities=capabilities)
```

An explicit missing method or disabled action/parameter raises
`UnsupportedConnectorOperation` (a `RemoteError` with status 501) before an RPC
is sent. Omitted fields mean **unknown**. Without discovery, native RPC errors
propagate unchanged; unknown support must not be shown as an enabled feature.
`supports(method)` returns `True`, `False`, or `None` for that method inventory,
not for every action the method may accept. Hermes's `gateway.capabilities`
does not enumerate connector methods; do not invent a discovery RPC or infer
support from a version string. A method list alone cannot prove new action or
parameter support.

The generated `client.gateway.connectors` API is pinned to the older full
OpenRPC snapshot identified in `contracts/sources.yaml`. It still has the old
session-only request signature. Use these dedicated wrappers for current hosted
account and owner-based operations; the older generated API is not silently
rewritten for every unrelated Hermes method in this release.

## Failure and catalog boundaries

No wrapper retries any call. A timeout, disconnect or cancelled local await can
leave a mutation accepted remotely. Reconcile the original operation via
`operation_status` or read the exact account/policy before deciding on another
mutation. Cancelling a coroutine does not send an implicit approval, denial,
remote cancel, reconnect or second connect. `wake_operation` tells the existing
watcher that the browser returned; it is not a connect retry. Calls return native
errors, including ownership, authentication, policy conflict and expired or
unknown-operation errors, without converting them into successful fixtures.

`lookup` preserves `found`, `invalid_name`, `unknown` and `unavailable` as
different results. A found entry carries the backend-reviewed SHA, repository
and subdirectory. It does not bypass plugin installation consent or its
capability review. `presence(names)` describes actual host requirements for the
requested catalog names, preserving the native order and omission of unknown
names. `onboarding()` returns an intentionally curated subset. Neither is a
full catalog search API. This release does not claim all catalog plugins can
load into every renderer or that a hosted provider account is authenticated.

Focused tests cover exact native request shapes, account/session/profile
ownership, old/new capability snapshots, stable opaque identities, native
status preservation, policy revision validation, credentials passed only to the
owning transport, timeout/disconnect/cancellation without replay, and catalog
action compatibility. Live account authorization needs an actual provider
identity and remains separate from transport/contract validation.

Verification for 0.34: all 568 SDK tests passed, including 44 focused connector
and catalog cases and a real TCP/WebSocket test against a simulated gateway.
Full Ruff and strict mypy checks passed. A separately isolated native Hermes
v0.22.0 instance also exercised these wrappers: known exact-SHA plugin lookup,
unknown lookup, ordered host presence, onboarding, session connector
availability, and preservation of native disabled-service errors for catalog,
accounts, tools and policy. Those disabled-service checks do not certify an
authenticated hosted account. Provider OAuth, account rename/removal and policy
mutation still require a deliberate live account test with credentials.
