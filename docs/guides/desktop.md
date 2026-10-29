# Desktop, connectors and workspaces

Hermes Desktop HTTP routes are separate from the control plane. This read-only example requires a running Desktop server, a concrete profile and any token required by that server:

```python
import asyncio
import os
from edith_hermes import AsyncHermesDesktop

async def main() -> None:
    async with AsyncHermesDesktop.remote(
        base_url=os.environ["HERMES_DESKTOP_URL"],
        profile=os.environ["HERMES_PROFILE"],
        token=os.getenv("HERMES_TOKEN"),
    ) as desktop:
        print(await desktop.capabilities())
        print(await desktop.cron.list())
        print(await desktop.skills.list())
        print(await desktop.git.worktrees(os.environ["PROJECT_PATH"]))

asyncio.run(main())
```

`desktop.cron` supports schedules and run history; `desktop.files`, `desktop.git`, `desktop.skills`, and `desktop.sessions.messages(session_id)` expose their respective native routes. Capabilities reflect the running server's route inventory, not every operation a deployment necessarily permits. Schedule mutations and triggers have side effects; after a timeout, reconcile saved state/history before trying again. See [Desktop API](../desktop-api.md).

For hosted connectors and the curated plugin catalog, use `AsyncHermesConnectors` and `AsyncPluginCatalog` with an authenticated native RPC connection and the exact owning profile. Discover deployment support where available; the generated older connector methods do not implement all newer account-based operations. See [hosted connectors](../hosted-connectors.md) for ownership, discovery and consent. Installing or connecting is a separate action from listing a catalog.

Native project and workspace methods are also available through `profile.native.projects` and `profile.native.session.workspace`. Their authority and support depend on the native server. Desktop Git worktrees and native projects are distinct operations; use opaque backend IDs for routing and check the relevant [Desktop bindings](../desktop-api.md) and [native contract](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/contracts/vendor/hermes/gateway-contract.openrpc.json) for exact parameters.
