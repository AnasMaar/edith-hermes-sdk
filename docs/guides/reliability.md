# Timeouts, retries and recovery

An application should retain instance, profile, session and turn IDs, handle errors, and reconcile state after an interrupted operation. A timeout tells you the client stopped waiting; it does not prove that server work stopped or failed.

## Control-plane HTTP

`Hermes.remote()` and `AsyncEdithHermes.remote()` default to a 30-second HTTP timeout and `max_retries=2`. The generated HTTP transport retries GET, HEAD and OPTIONS, and operations carrying an idempotency key, on transport errors or HTTP 429, 502, 503 and 504. Other mutations are sent once. Contract operations that support an idempotency key generate one when omitted; pass your own stable `idempotency_key` when your application must reconcile or retry the same logical operation across calls. Server behavior still determines the idempotency guarantee.

`turn.wait(timeout=...)` polls until a terminal state or pending approval. Its timeout does not cancel the turn. Inspect `turn.get()` or explicitly call `turn.stop()` when appropriate. A session event stream is not automatically retried or filtered to one turn. After answering an approval, wait again; the native server may take time to process it.

## Native gateway and Desktop

`profile.connect()` has no automatic reconnect or replay. The connection fails pending calls on disconnect and closes on event-queue overflow rather than silently dropping requests. Reconnect deliberately, inspect active session state, and decide whether a write is safe to repeat. Native server requests must be answered on their originating connection. A `connection.call()` timeout does not cancel native work.

Desktop mutations are sent once by the SDK. After a timeout, inspect saved state or history before repeating an operation. A timeout during an installer, schedule trigger, or other mutation can leave its outcome uncertain. The optional receipt-based extensions have additional capability and recovery requirements; see [Desktop API](../desktop-api.md).

## Error handling and borrowed clients

HTTP errors map to SDK exceptions such as `AuthenticationError`, `NotFoundError`, `ConflictError`, and `RemoteError`; transport and timeout errors can also propagate. Do not interpret a discovery or authentication failure as an empty successful result. If you supply an `httpx.AsyncClient`, you own its configuration and lifetime. See [architecture](architecture.md) for ownership and [configuration](../configuration.md) for deployment constraints.
