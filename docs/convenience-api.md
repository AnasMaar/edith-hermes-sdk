# Convenient API: coverage and behavior

This API ships in the 0.4.0 source; older published artifacts do not supply it. `Hermes` is the primary
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

`Agent` accepts annotated Python functions or `@tool` objects. `max_turns`, `toolsets`
and `config` configure the native profile; `profile_options` and `session_options`
remain available for the complete underlying contract. Invalid tools and duplicate
names fail before provisioning. `agent.open_session(id)` checks instance/profile
ownership before selecting an existing conversation. `add_tools(functions)` and
`remove_tools(binding_id)` support a running profile without recreating its instance;
these operations are serialized with the bound agent's runs and session selection.
Separate handles/processes are not implicitly serialized with each other.

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

The coverage manifest exactly matches **72 HTTP operations and 219 native RPC
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
  transport are available. See the [WebSocket contract](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/contracts/websocket/gateway.md)
  for explicit server-request replies, lifecycle rules, and bridge upgrade requirements.
- Runtime-provider availability, profile/session action semantics, per-turn
  tools, image publication, and MCP OAuth still depend on backend/native support.
  A generated method does not repair all pre-existing server implementation gaps.
  See the [latest verification report](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/docs/verification-2026-09-30.md) for repaired
  adapters and explicitly unsupported overrides.
- Live Docker, Kubernetes, Linux-process and PostgreSQL checks are recorded in
  the [latest verification report](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/docs/verification-2026-09-30.md). Real local-model
  execution now reaches the Python callback, including dynamically added tools.
  Earlier failures remain in the historical reports; lifecycle checks alone
  are still not evidence of successful reasoning or arbitrary model compatibility.

Pool leases are reserved atomically in SQLite/PostgreSQL, with expiry and protection
against an old lease releasing a newer one. Required labels and existing-profile
scope are enforced. Pool size changes and deletion must use one controller; no
multi-writer reconciler or automatic idle-eviction certification is claimed.
StatefulSet mapping, idle TTL automation and custom strategies are rejected explicitly.
Round-robin, sticky-key, random and stored-session/busy-turn ordering are implemented;
the latter are registry snapshots, not live cluster-utilization metrics.

Build the Kubernetes bridge from the same checkout and explicitly select its image
through `EDITH_RUNTIME_BRIDGE_IMAGE`. The old v0.3.1 deployment example/bridge image
is not the new duplex implementation, and this source push does not publish a new image.

Model-provider authentication is now available under every profile's `providers`:
`login = await agent.providers("openai-codex").login()`, followed by `login.wait()`.
See [provider authentication](provider-auth.md) for the complete auth surface, credential
custody rules, external-flow compatibility and live/protocol verification boundaries.

The existing runnable examples were left unchanged during this convenience-layer
expansion so application-specific examples can be authored independently.
