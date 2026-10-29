# Authentication and credentials

There are separate credentials for the control plane, native Desktop, model providers and hosted connectors. A control-plane bearer token does not log a profile into a model provider.

## Control plane and Desktop

Pass `token=` to `Hermes.remote(base_url, token=...)` or `AsyncEdithHermes.remote(base_url=..., token=...)` when the control plane requires a bearer token. `AsyncHermesDesktop.remote(base_url=..., profile=..., token=...)` takes a Desktop token for its own HTTP server. Supply secrets from the environment or a secret manager instead of committing them. Local control-plane authentication can be configured as `none`, `static`, or `oidc`; see [configuration](../configuration.md).

## Model provider login

For an SDK-managed instance, select the bound profile and inspect the provider before starting login:

```python
# Contextual excerpt: hermes is a connected Hermes client and instance_id is known.
instance = await hermes.open_instance(instance_id)
agent = instance.agent("Assistant")
provider = agent.providers("openai-codex")
print(await provider.status())
login = await provider.login()
print(login.verification_url, login.user_code)
result = await login.wait()
print(result)
```

Login requires the user's action at the provider, and does not select a model. After verifying support and entitlement, configure the profile separately with `await agent.update(provider="openai-codex", model=model_id)`. The [provider authentication guide](../provider-auth.md) covers polling, cancellation, error handling and credential custody. Provider support and actual login flow depend on the deployment.

## Connectors and tools

Hosted connector authentication and tool-execution approval are separate decisions. Connector wrappers preserve owner and profile scope; see [hosted connectors](../hosted-connectors.md). For a remote Python `ToolHost`, advertise a URL reachable by the control plane, use HTTPS off-machine, and treat its capability callback URLs as secrets. Closing the SDK client does not stop an independently served host.
