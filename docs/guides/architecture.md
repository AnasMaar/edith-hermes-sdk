# Architecture and resource ownership

An application talks to the EDITH control plane to manage instances, profiles, sessions, turns, tools and provisioning jobs. The control plane routes each instance to its runtime provider and native Hermes gateway. Separately, `AsyncHermesDesktop` talks to native Desktop HTTP routes; its endpoint and supported operations are different from the control plane's.

```text
Python application ── Hermes / AsyncEdithHermes ── EDITH control plane ── Hermes runtime
                   └─ AsyncHermesDesktop ────────── Hermes Desktop HTTP
```

`Hermes` exposes convenient resource handles and wraps an `AsyncEdithHermes` client at `hermes.sdk`. The generated low-level namespaces expose the checked-in control-plane and native contracts; a signature in the SDK does not establish that a running server implements it. Native administration methods can be instance-wide even when called through a profile handle.

## IDs and handles

An instance has profiles, and a control-plane profile has control-plane sessions and turns. Use the exact IDs returned by the deployment. Calling `hermes.instances(instance_id).profiles(profile_id)` constructs a scoped handle without fetching or creating resources; call `await profile.get()` to retrieve it. Display names are not routing IDs.

Native Hermes sessions have their own IDs. `profile.native.session.list()` returns native sessions, and `profile.connect()` communicates on a persistent gateway connection. A control-plane session may refer to a native session via `profile.sessions.create(resume_native_session_id=native_id)`; do not substitute one ID for the other. See [native chat](native-chat.md).

## Lifecycle and optional services

`Hermes.local()` starts a local control plane and tool host. By default, it deletes instances created in that context on exit; `cleanup=False` retains them. `open_instance()` attaches to an existing instance without taking cleanup ownership. Callback tools hosted by that local context stop being reachable when the host exits. `Hermes.remote()` closes client connections on exit but does not delete instances. Remote Python tools require a separately served `ToolHost` reachable from the control plane.

For `AsyncEdithHermes.remote(http_client=...)` and `AsyncHermesDesktop.remote(http_client=...)`, the caller owns the supplied HTTP client and must close it. Each client closes an HTTP client it created itself; Desktop's `for_profile()` shares the original client and does not take ownership. An embedded driver is closed when its SDK client closes.

Desktop extensions, hosted connectors, and plugin catalog wrappers depend on matching backend capabilities. They are separate from the pinned generated native RPC catalog; discover support rather than assuming every deployment exposes them. See [Desktop and integrations](desktop.md).
