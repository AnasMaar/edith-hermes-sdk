# Runnable SDK examples

Run these from the repository root. Install the SDK with streaming support, for example:

```console
python -m pip install -e ".[streaming]"
python examples/local_tool.py
```

The tool example is entirely local and prints a tool schema and `result: 2`. The other scripts need a running deployment and access to a **dedicated sandbox** instance/profile. They do not choose or create a default profile. Use actual IDs returned by your deployment, and keep tokens out of commands and files. In PowerShell, for example:

```powershell
$env:EDITH_TOKEN = '<control-plane token>'
$env:HERMES_DESKTOP_TOKEN = '<desktop token, if required>'
```

`--url` means the control-plane HTTP URL except in `desktop_schedules.py`, where it means the direct Hermes Desktop HTTP URL. Tokens are optional if your deployment does not require them. The control-plane `--profile` is the profile ID; the connector and schedule examples resolve its native profile name before calling profile-scoped APIs. Native examples require the control plane's authenticated WebSocket gateway and a compatible native runtime; extension APIs depend on deployment capabilities. Unsupported methods and connection/authentication errors are reported by the SDK.

```console
python examples/control_plane_inventory.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE
python examples/native_inventory.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --plugin calendar
python examples/desktop_schedules.py --url https://DESKTOP --profile PROFILE
python examples/approval.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --session SESSION
```

These print JSON: respectively instances and sessions; native sessions, background agents, groups, a plugin catalog lookup and connectors; scheduled jobs; and pending approvals. The native inventory includes both HTTP RPC and persistent WebSocket calls. Returned content may be sensitive; avoid sharing logs. Catalog lookup is discovery, not installation or an installed-plugin inventory.

The following writes require `--run`. Use an isolated sandbox room/profile and test file. Prompts, bot messages, and group messages can trigger model inference and charges. The bot example uses the native `bot_relay.deliver` method, which blocks for a one-turn reply. The attachment script stages bytes and sends the returned attachment ID to the selected room; it prints both IDs for inspection.

```console
python examples/native_events.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --prompt "Say hello" --run
python examples/schedule_create.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --name "SDK example" --prompt "Review notes" --schedule "every 2h" --run
python examples/bot_message.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --message "Say hello" --run
python examples/group_attachment.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --room ROOM --file ./note.txt --message "Read this" --run
python examples/approval.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --session SESSION --request REQUEST --choice deny --run
```

The event example prints up to `--limit` frames and waits at most `--timeout` seconds per frame. After each frame it checks session-scoped replay from the pre-submit cursor for `message.complete`. Idle timeout, disconnection, replay gaps, or the frame limit leave the turn status uncertain; inspect the session before retrying. It leaves server requests unanswered: an interactive application must inspect them and explicitly respond on the same connection, using the appropriate protocol. To decide a command approval, inspect the pending request first and supply its exact session and request IDs and your decision (`once`, `session`, or `deny`) to the approval example. Do not infer approval from receipt of an event.

The schedule example creates a paused job and prints its request ID before dispatch. If creation times out, it queries the matching receipt once; a pending, uncertain, or failed lookup still requires inspection before any retry. Delete the sandbox job through your deployment when finished.

The event example requests `close_on_disconnect=False` so leaving the viewer does not request cancellation. The session and transcript can persist: inspect active work, close the session, then delete the stored transcript using your deployment's session management if desired. Group messages and staged attachments remain in the selected room; remove them through the deployment's management tools if supported. The bot message remains in Bot Chat. Closing the SDK client does not undo these writes. If a write times out, its outcome can be uncertain; inspect the target before retrying.

## Offline verification

From a development checkout with the project's dev dependencies installed:

```console
python -m pytest tests/test_documented_examples.py
```

The tests run the example functions against isolated `httpx.MockTransport`, an embedded driver, and a local simulated WebSocket server. They check requests, scoped IDs, events, and attachment bytes; they do not contact a live deployment or model. A passing fixture test does not establish that your deployment supports every method or has a configured model. The older provisioning and deployment examples in this directory have their own prerequisites and may create resources; inspect them before running.
