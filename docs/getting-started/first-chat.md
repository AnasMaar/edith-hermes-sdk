# First chat with an existing profile

This walkthrough creates a control-plane session, sends a prompt, and prints the result. It requires a running EDITH control plane, an instance registered and ready there, and a profile configured with a working model and provider credentials. Use a dedicated test profile: a prompt may execute tools and incur model charges. The SDK does not provide a model or credentials itself.

Install the SDK from the checkout: `python -m pip install .`. Ask the deployment administrator for the control-plane URL and its opaque instance and profile IDs. The URL is the control-plane HTTP endpoint, not the Desktop server or a native WebSocket URL. Set these values in your shell, adding a token only when required.

=== "Bash"

    ```bash
    export EDITH_CONTROL_URL="https://your-control-plane"
    export EDITH_INSTANCE_ID="your-instance-id"
    export EDITH_PROFILE_ID="your-profile-id"
    export EDITH_TOKEN="your-control-plane-token" # omit for an unauthenticated deployment
    ```

=== "PowerShell"

    ```powershell
    $env:EDITH_CONTROL_URL = 'https://your-control-plane'
    $env:EDITH_INSTANCE_ID = 'your-instance-id'
    $env:EDITH_PROFILE_ID = 'your-profile-id'
    $env:EDITH_TOKEN = 'your-control-plane-token' # omit if not required
    ```

Save the following as `first_chat.py` and run `python first_chat.py`:

```python
import asyncio
import os
from edith_hermes import Hermes

async def main() -> None:
    async with Hermes.remote(os.environ["EDITH_CONTROL_URL"], token=os.getenv("EDITH_TOKEN")) as hermes:
        profile = hermes.instances(os.environ["EDITH_INSTANCE_ID"]).profiles(os.environ["EDITH_PROFILE_ID"])
        session = await profile.sessions.create(title="SDK first chat")
        session_id = session["id"]
        print("Session ID:", session_id)
        conversation = profile.sessions(session_id)
        submitted = await conversation.turns.submit(content="Say hello in one sentence.")
        print("Turn ID:", submitted["id"])
        turn = conversation.turns(submitted["id"])
        result = await turn.wait(timeout=120)
        print("Status:", result["status"])
        for part in result.get("output", []):
            if part.get("type") == "text":
                print(part.get("text", ""))
        if result["status"] == "waiting_for_approval":
            print("A user decision is required; inspect the pending request before proceeding.")

asyncio.run(main())
```

The result may be `completed`, `failed`, `stopped`, or `waiting_for_approval`. Review the full returned state for failures and approval details. A timeout does not stop a turn; retain the printed session and turn IDs so you can inspect it.

## Reopen and continue

Save the control-plane session ID. In a later process, select it with `conversation = profile.sessions(session_id)`, verify ownership and state with `await conversation.get()`, and submit another turn through `conversation.turns.submit(content="...")`. Selecting a handle does not fetch or create anything. A control-plane session ID is distinct from a native Hermes session ID; see [architecture](../guides/architecture.md).

If a turn needs approval, inspect the actual request and obtain the user's decision. The turn handle accepts `await turn.approve(request_id, "allow_once")`, `"allow_session"`, or `"deny"`. Wait again after the answer; the server may briefly still report the pending state. For native server requests and native approvals, see [native chat](../guides/native-chat.md). Do not auto-approve requests.

## Configure the model

The walkthrough expects the selected profile to already have a provider, model, and credentials. If you administer a dedicated profile, choose provider and model IDs supported by that deployment and set `HERMES_PROVIDER` and `HERMES_MODEL` in your shell, using `export` in Bash or `$env:... = '...'` in PowerShell. Within the connected context, this explicit mutation saves those settings:

```python
# Contextual excerpt: profile is the dedicated profile selected above.
await profile.update(provider=os.environ["HERMES_PROVIDER"], model=os.environ["HERMES_MODEL"])
```

This changes persistent profile configuration, not a temporary per-turn option. Provider login is separate from control-plane authentication; see [authentication](../guides/authentication.md) and [provider login](../provider-auth.md). For custom endpoints, make sure the runtime can reach the endpoint from its own network.

## Cleanup

Closing `Hermes.remote()` closes the SDK connections; it does not delete the session or instance. If the test session should be removed, call `await conversation.delete()` while connected, after checking your application's retention needs. Provisioned instances require explicit lifecycle management; [runtime choices](../guides/runtimes.md) explains local cleanup.
