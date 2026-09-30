# Convenient API: coverage and behavior

This working-tree API is not yet a published release. `Hermes` is the primary
entry point; `AsyncEdithHermes` remains supported for existing applications.
Both use the same transports and backend. No database, Kubernetes cluster,
authentication scheme, or KMS is imposed by the client.

## Resource paths

Calling a collection with an ID selects a lightweight handle; it does not fetch,
create, or adopt a runtime. Await `get()` to retrieve its current server state.
`open_instance()` additionally reconstructs named agent handles. `create_instance()`
provisions and waits, while `instances.create()` is the direct contract operation.

| Resource path from `hermes` | Operations |
| --- | --- |
| `capabilities()` | Control-plane capabilities |
| `instances` / `instances(id)` | List, create, get, update, delete, action, connection, capabilities |
| `instances(id).profiles` / `profiles(profile_id)` | List, create/clone, get, update, delete; typed native methods |
| `…profiles(profile_id).sessions` / `sessions(session_id)` | List, create, get, delete, actions, SSE events |
| `…sessions(session_id).turns` / `turns(turn_id)` | Submit, get, wait, action, stop, steer, approve |
| `pools` / `pools(id)` | List, create, get, update/scale, delete |
| `pools(id).leases` / `leases(id)` | Acquire and release leases |
| `jobs` / `jobs(id)` | Provision user instance; get and wait |
| `images.recipes` / `recipes(id)` | List, create, get, delete recipes |
| `images.builds` / `builds(id)` | List, start, get, cancel, wait; stream logs |
| `images` / `images(id)` | List, get, delete managed images |
| `tools.bundles` / `bundles(id)` | List, create, get, replace, delete |
| `tools.bindings` / `bindings(id)` | List/filter, create, get, delete |
| `tools.mcp_servers` / `mcp_servers(id)` | List, create, get, replace, delete, actions |
| `tools.call()` | Execute a scoped tool call |
| `inference.chat()` / `inference.complete()` | Vendored Nous inference operations |

The `Instance` returned by `create_instance()` also exposes all instance-resource
methods. A `BoundAgent` exposes all profile-resource methods, including `sessions`
and `native`; IDs need not be repeated. `agent.session` selects its active session
after `new_session()`, `start()`, or `run()`.

`agent.start(prompt)` returns a turn handle without waiting. `agent.run(prompt)`
waits for completion, failure, interruption, or a pending approval and returns
`RunResult`. Both expose tool-binding IDs, metadata, and idempotency keys.
Use `session.events()` for the session SSE stream (including concurrent turns);
the stream is not implicitly filtered to a particular turn.
`wait()` timing out does **not** cancel server work. `turn.stop()` is explicit.
After answering an approval, call `wait()` again. A still-pending request may
return immediately until the native server processes the answer.

## Native Hermes methods

Every method in the pinned OpenRPC catalog has a discoverable method under
`profile.native`. Dots become namespace navigation: `mcp.servers.list` becomes
`agent.native.mcp.servers.list()`, and `approval.respond` becomes
`agent.native.approval.respond(session_id=..., request_id=..., choice=...)`.

Parameters and results are typed from that catalog. Results unwrap the JSON-RPC
envelope; `.rpc(...)` and `.request(...)` retain the raw compatibility behavior.
Native methods that also have child methods use `_call` on the leaf invocation
to avoid masking their namespace, e.g. `native.pet.info_call(...)` versus
`native.pet.info.<child>(...)`. Consult editor completion or the generated
coverage manifest for the exact path.

Instance/profile routing IDs are bound to the object. The backend injects the
native profile name only for methods whose schema accepts `profile`. This does
not turn an instance-wide native operation into a profile-isolated operation:
native administrative methods retain their upstream scope and authority.

## Typing and extensions

Public keyword arguments use snake_case. Nested wire dictionaries retain the
contract's keys (for example `tenantId`, `subjectId`, and `recipeId`). Their
TypedDict types are available through `edith_hermes.models.control_plane`,
`.images`, `.runtime`, `.tools`, `.inference`, and `.native`.

The generated methods carry explicit signatures, required arguments, literal
choices, nested object types, and return shapes. These are static types, not
runtime response validation or a guarantee that the server implements a field.
Unknown JSON and open extension values intentionally remain `Any`.

Omitting an optional field differs from passing `None`: omission leaves server
defaults intact; explicit null is transmitted. `extra_body` and `extra_params`
allow forward-compatible fields without replacing explicit arguments. Duplicate
fields raise an error. Bound native profile routing cannot be overridden through
`extra_params`. Merge-patch updates preserve their declared request fields.

`Hermes.create_instance()` accepts a per-call runtime and owner plus additional
provisioning `options`, without silently replacing name/runtime/bootstrap fields.
Use `jobs.create()` for direct, fully typed provisioning-contract control.

## Remote Python tools

`Hermes.local()` starts and stops its tool listener automatically. For a remote
control plane, construct `ToolHost(base_url=...)`, serve its `.app` using an ASGI
server, and pass `tool_host=host` to `Hermes.remote()` or `Hermes(sdk, ...)`.
Install the `control-plane` extra for FastAPI hosting dependencies.

The URL must be reachable **from the control plane**, not merely from your SDK
process. If mounting below a path prefix, include that prefix in the advertised
URL. Serving and TLS are the application's responsibility. Register tools before
making calls, keep the host alive, and use sticky routing or a shared tool registry
if deploying multiple workers: the supplied registry lives in one process.

Only unguessable capability-URL callbacks are exposed. Treat those URLs as secrets,
use HTTPS off-machine, and redact access logs. `host.unregister(callback_url)`
revokes a registration. This host does not expose anonymous control-plane routes.
Closing a remote `Hermes` client closes connections, not instances or your tool host.

## Completeness boundary and verification

The coverage manifest exactly matches **64 HTTP operations and 219 native RPC
methods in the checked-in contracts**. Regeneration fails if an HTTP operation
lacks a resource mapping. Tests invoke every generated operation, resolve its
annotations on Python 3.10, traverse every native namespace, check routing and
wire mapping, and exercise extensions, streams, timeouts, callbacks, and errors.
The server turn-action adapter now maps stop/steer/approval to the proper native
methods and checks that the turn belongs to the selected session/profile.

Coverage means API parity with these contracts, not that all Hermes deployments
implement every capability. In particular:

- Arbitrary cloud-provider extensions remain `hermes.cloud.invoke(...)`; there
  is no vendored authoritative typed cloud-management contract.
- SQLite/PostgreSQL remain backend implementation choices; this change does not
  create an arbitrary database/table ORM or additional storage drivers.
- Typed native approval/clarification methods and a persistent `profile.connect()`
  transport are available. See the [WebSocket contract](../contracts/websocket/gateway.md)
  for explicit server-request replies, lifecycle rules, and bridge upgrade requirements.
- Runtime-provider availability, profile/session action semantics, per-turn
  tools, image publication, and MCP OAuth still depend on backend/native support.
  A generated method does not repair all pre-existing server implementation gaps.
  See the [latest verification report](verification-2026-09-25.md) for repaired
  adapters and explicitly unsupported overrides.
- Live Docker, Kubernetes, Linux-process and PostgreSQL checks are recorded in
  the [latest verification report](verification-2026-09-25.md). Earlier evidence
  remains in `local-verification.md`. The actual local-model tool-execution
  check failed; passing lifecycle checks do not certify a successful model turn.

The existing runnable examples were left unchanged during this convenience-layer
expansion so application-specific examples can be authored independently.
