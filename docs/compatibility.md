# Support and compatibility

## SDK and runtime are separate versions

This documentation describes SDK **0.35.0**, with Python **3.10–3.14** support.
The SDK wraps several independent services, so one SDK version cannot promise that
every Hermes deployment supports every method.

| Surface | Contract or implementation | Availability check |
| --- | --- | --- |
| Control-plane resources | Versioned OpenAPI and generated SDK | Running control plane and its deployed routes |
| Native RPC | Pinned Hermes gateway contract | Runtime version and supported native methods |
| Native Desktop HTTP | Explicit bindings to Desktop REST routes | The profile-bound client's capabilities |
| Hosted connectors and curated catalog | Inspected Hermes v0.22.0 owner/account APIs | Discovery plus method-specific errors |
| EDITH backend extensions | Explicit application-owned versioned operations | Extension capabilities on the running host |
| Cloud management | Generic invocation surface | A separately configured, supported cloud adapter |

Native source snapshots and hashes are recorded in
the [Hermes contract manifest](https://github.com/AnasMaar/edith-hermes-sdk/tree/main/contracts/vendor/hermes).
A snapshot records which interface was inspected. It does not install that server,
grant account entitlements or establish that another release implements the same interface.

## Python and optional dependencies

The base client depends on HTTPX, Pydantic and typing extensions. Install extras only
for the workflows you use:

| Installation | Adds |
| --- | --- |
| Base package | HTTP clients, typed interfaces and tool definitions |
| streaming extra | WebSocket support |
| control-plane extra | In-process server, persistence and runtime-provider dependencies |
| embedded extra | Docker and Kubernetes integration dependencies |

See [installation](getting-started/installation.md) for source and wheel commands.
An extra installs Python dependencies; it does not install Docker, Kubernetes, model weights
or the Hermes command-line program.

## Deployment support is discovered, not inferred

An unsupported operation, an authentication error and a disconnected server are
different conditions. Keep those distinctions in your application's error handling.
Do not turn failed discovery into an empty successful inventory.

Preserve the owning connection, instance, profile and canonical resource ID when
aggregating several runtimes. Equal display names do not identify the same resource.

## Evidence and limits

The [verification report](release/verification.md) separates unit/protocol fixtures,
package checks and live prerequisites. Desktop operating-system features, physical audio,
provider sign-in and actual model behavior require the relevant running services and devices.
There is no claim of complete native Hermes Desktop coverage.
