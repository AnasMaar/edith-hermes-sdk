# Runtimes, tools and models

`Hermes` manages resources through an EDITH control plane. Choose a runtime supported by that control plane:

| Runtime | Use | Requirements and ownership |
| --- | --- | --- |
| `Docker(image=...)` | Local or remote container | Docker-compatible engine; control plane creates and removes container and volume |
| `Process(executable="hermes")` | Local child process | Installed Hermes executable; control plane starts and terminates it |
| `External(endpoint=...)` | Adopt an existing runtime | Reachable bridge HTTP URL or native WebSocket; external supervisor owns its lifecycle |
| `Kubernetes(image=..., namespace=...)` | Cluster workload | Enabled Kubernetes provider and configured cluster; use a compatible bridge image |

For example, `async with Hermes.local(runtime=Process()) as hermes:` uses a locally installed executable. `Hermes.remote("https://control.example", token=token, runtime=Docker(image="your-image"))` uses the remote control plane's Docker provider, not the caller's Docker engine. Pass deployment-specific values and ensure the server enables that provider. `External` registers an existing endpoint; it does not start the native process. See [configuration](../configuration.md) for settings, authentication and ownership details.

## Python tools

An `Agent` accepts annotated Python functions or `@tool` objects. Definitions are validated before provisioning. `Hermes.local()` runs a callback host automatically; for a remote control plane, create `ToolHost(base_url=...)`, serve its `app` with an ASGI server and pass `tool_host=host` to `Hermes.remote()`. The advertised URL must be reachable from the control plane. Keep the host alive while tools are used; callback URLs are secrets. See [remote Python tools](../convenience-api.md#remote-python-tools).

A bound agent can add and remove tools with `await agent.add_tools([function])` and `await agent.remove_tools(binding_id)`. Separate processes or handles are not implicitly serialized.

## Profiles and models

`Agent(name, instructions=..., model=..., tools=...)` describes a profile; creating an instance attaches it. `instance.agent(name)` returns its bound handle. `await hermes.open_instance(instance_id)` reconstructs handles for an existing SDK-managed instance. A session belongs to a profile; `await agent.new_session(title="...")` selects a new one, while `await agent.open_session(session_id)` checks ownership before selecting an existing control-plane session.

Use `Model(id, provider=..., base_url=..., api_key=...)` for explicit model settings, or configure credentials through the native provider flow. The model endpoint must be reachable from the runtime, and availability depends on the provider and account. For OAuth and selecting a model after login, see [provider authentication](../provider-auth.md). Never embed real credentials in source code.
