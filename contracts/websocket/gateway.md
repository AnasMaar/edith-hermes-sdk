# Persistent native gateway transport

This supplements (not replaces) the HTTP OpenAPI contracts. WebSocket messages
use the pinned `vendor/hermes/gateway-contract.openrpc.json` catalog.

## Endpoints and authorization

- Control plane: `GET /v1/instances/{instanceId}/profiles/{profileId}/gateway`
  with WebSocket upgrade. Uses the same authorization headers/owner identity as
  HTTP. Before upgrading, the server verifies ownership, profile/instance
  association, and instance readiness. Authentication is not passed in query strings.
- Runtime bridge: `GET /ws` with WebSocket upgrade. Requires
  `Authorization: Bearer <EDITH_BRIDGE_TOKEN>` when configured. This is an internal
  service endpoint, not a public anonymous management API.

An accepted connection begins with a JSON-RPC `event` notification whose
`params.type` is `gateway.ready`. The relay then carries bidirectional JSON text
frames. Profile-scoped native method parameters are overwritten with the selected
native profile name; administrative instance-wide methods retain native scope.
This is not a per-profile sandbox or a restricted RPC allow-list.

## Messages

- Client calls: `{"jsonrpc":"2.0","id":"unique-id","method":"...","params":{...}}`.
- Responses: same ID with `result` or `error`.
- Notifications: native `method`/`params` with no request ID.
- Server requests: native `method`/`params` **and an ID**. The client must send
  a response with that exact ID on the same connection. A notification/event
  stream alone cannot respond to these requests.

The SDK sends `client.capabilities` with `server_requests: true` on connection.
It never automatically grants approval, answers a question, or provides secrets.
`NativeConnection.respond()` requires a received, unanswered request ID.

SDK entry point: `async with profile.connect() as connection`. `call()` sends a
native RPC; `events()` has one consumer and yields notifications/server requests;
`respond()` answers a server request. Replies to concurrent calls are correlated
by unique IDs. Calls timing out do not cancel native work. Disconnect fails pending
calls. The bounded event queue closes on overflow rather than silently continuing
after dropping a potentially important request. There is no automatic reconnect
or replay; an application must reconcile active sessions before retrying writes.

Remote clients install `edith-hermes-sdk[streaming]`. In-process clients already
require the `control-plane` extra and connect through the native gateway adapter.
The Kubernetes bridge image must be rebuilt/deployed to provide the new `/ws`
endpoint; an old deployed bridge does not gain it from a client-only upgrade.
