# Existing native sessions and events

The SDK's persistent native gateway connection is reached through an EDITH control-plane profile. It is not a direct `AsyncEdithHermes` connection to an arbitrary native WebSocket. Register/adopt the runtime with the control plane first and obtain its instance and profile IDs. Remote gateway streaming needs the `streaming` extra and a compatible control-plane/bridge deployment.

```python
import asyncio
import os
from edith_hermes import Hermes

async def main() -> None:
    async with Hermes.remote(os.environ["EDITH_CONTROL_URL"], token=os.getenv("EDITH_TOKEN")) as hermes:
        profile = hermes.instances(os.environ["EDITH_INSTANCE_ID"]).profiles(os.environ["EDITH_PROFILE_ID"])
        print(await profile.native.session.list(limit=10))
        async with profile.connect() as connection:
            session_id = os.environ["HERMES_SESSION_ID"]
            print(await connection.call("session.resume", session_id=session_id))
            print(await connection.call("prompt.submit", session_id=session_id, text="Hello again"))
            async for frame in connection.events():
                print(frame)
                # Your UI must interpret native completion and request frames.

asyncio.run(main())
```

The loop is intentionally long-lived: stop it according to your application's native completion and shutdown policy. `session.resume` and `prompt.submit` use a **native** session ID. Control-plane session IDs are separate; `profile.sessions.create(resume_native_session_id=...)` creates a control-plane session referring to a native one.

`events()` has one consumer and yields notifications and server requests. A server request has a `method` and an `id`. Answer it on the same connection using `await connection.respond(frame["id"], result=answer)` only after interpreting the specific native request and collecting any required user decision. The SDK does not automatically grant approvals. Native approval RPC also exposes `profile.native.approval.pending(session_id=...)` and `profile.native.approval.respond(session_id=..., request_id=..., choice=...)`; choices and requests must come from the running native server's contract. These mechanisms are distinct from `turn.approve()` on a control-plane turn.

Connection loss fails pending calls; there is no automatic reconnect or replay. Reconcile session state before retrying a write. Timeouts do not cancel native work. See the [gateway contract](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/contracts/websocket/gateway.md) for lifecycle and bridge requirements.
