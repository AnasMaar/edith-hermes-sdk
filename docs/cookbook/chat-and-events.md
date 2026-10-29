# Chat and events

Use a sandbox instance and profile with a configured provider and model for the live prompt. Install the streaming extra, set `EDITH_TOKEN` if required, and use the control-plane URL and opaque instance/profile IDs. The inventory command is read-only; it prints instance and session data:

```console
python examples/control_plane_inventory.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE
```

[Download control_plane_inventory.py](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/examples/control_plane_inventory.py)

```python
--8<-- "examples/control_plane_inventory.py"
```

To create a native session, submit a prompt, and receive frames over the same connection:

```console
python examples/native_events.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --prompt "Say hello" --run
```

This may incur model charges and execute tools. It prints the session and up to `--limit` event frames, waiting at most `--timeout` seconds for each. After each frame it checks session-scoped replay from the cursor captured before submission for `message.complete`, then prints the resulting status. Idle timeout, disconnection, replay gaps, or the frame limit leave the turn status uncertain; inspect the session before retrying. Server requests are printed and left unanswered. An interactive application must examine each request and respond on its originating connection according to its method. The session uses `close_on_disconnect=False`, so exiting the viewer does not request cancellation. The session and transcript can persist; inspect any active work and close the session, then delete the stored transcript through your deployment when finished.

[Download native_events.py](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/examples/native_events.py)

```python
--8<-- "examples/native_events.py"
```

For native command approvals, first inspect pending requests on the exact native session:

```console
python examples/approval.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --session SESSION
```

After reviewing a request and obtaining a decision, pass its exact request ID with `--request REQUEST --choice deny --run`. Supported example choices are `once`, `session`, and `deny`; a decision can permit a command to run. This operation is distinct from responding to an arbitrary WebSocket server request.

[Download approval.py](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/examples/approval.py)

```python
--8<-- "examples/approval.py"
```
