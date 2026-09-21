# EDITH Hermes SDK

`edith-hermes-sdk` is the Python control surface for building, provisioning, and operating
user-owned Hermes runtimes. It supports a remote control plane and embedded drivers through the
same API. Version 0.1 provides the complete generated interface plus a persistent mock platform;
real BuildKit and Kubernetes reconciliation are the next production milestone.

## Install and use

```bash
uv add ./dist/edith_hermes_sdk-0.1.0-py3-none-any.whl
```

```python
from edith_hermes import AsyncEdithHermes

async with AsyncEdithHermes.remote(
    base_url="http://localhost:8080",
    token="dev-user-1",
) as sdk:
    instances = await sdk.control_plane.list_instances()
```

Start the persistent mock server with:

```bash
docker compose -f deploy/compose.yaml up --build
```

The default development identities are `dev-user-1` and `dev-user-2`. Override
`EDITH_MOCK_TOKENS` with a JSON token-to-owner map outside local development.

This repository defines a contract-first SDK for controlling one or many Hermes Agent runtimes.

The SDK is generated from two kinds of contracts:

1. **Upstream Hermes contracts** remain authoritative for native behavior. In particular, the
   Hermes TUI/Desktop gateway OpenRPC document supplies every native JSON-RPC method, event,
   server request, and schema.
2. **SDK contracts** add resource-oriented interfaces that Hermes does not provide as one API:
   instance provisioning, profiles addressed through a specific instance, pools, Kubernetes
   placement, connection discovery, session routing, and dynamic tool attachment.

Keeping both layers is intentional. Re-expressing all Hermes JSON-RPC methods as hand-written
OpenAPI operations would create a second, lossy contract that could drift from Hermes.

## Contract set

| Contract | Purpose |
| --- | --- |
| [`contracts/sources.yaml`](contracts/sources.yaml) | Pinned upstream contracts and SDK namespace/coverage map |
| [`contracts/openapi/images.openapi.yaml`](contracts/openapi/images.openapi.yaml) | Managed recipes, isolated builds, image verification and registry publication |
| [`contracts/openapi/control-plane.openapi.yaml`](contracts/openapi/control-plane.openapi.yaml) | Instances, lifecycle, profiles, pools, leases, Kubernetes and connection descriptors |
| [`contracts/openapi/runtime.openapi.yaml`](contracts/openapi/runtime.openapi.yaml) | Instance/profile-scoped sessions, turns, event streams, capability discovery and native RPC escape hatch |
| [`contracts/openapi/tools.openapi.yaml`](contracts/openapi/tools.openapi.yaml) | Dynamic tool bundles, bindings, MCP servers and tool execution callbacks |

## Target hierarchy

Every stateful SDK call resolves an explicit target:

```text
instance
└── profile
    └── session
        ├── turn
        └── subagent
```

An instance is a running Hermes backend. A profile is an isolated Hermes configuration and data
home within that backend. A session is a conversation owned by a profile. Pools contain instances
and may allocate leases for workload routing.

## Feature-complete SDK generation

The generated SDK should expose:

```text
sdk.controlPlane     generated from control-plane.openapi.yaml
sdk.images           generated from images.openapi.yaml
sdk.runtime          generated from runtime.openapi.yaml
sdk.tools            generated from tools.openapi.yaml
sdk.gateway          generated from upstream gateway-contract.openrpc.json
sdk.inference        generated from the Nous inference OpenAPI document
sdk.cloud            generated/discovered from the Nous Portal MCP server
```

`sdk.gateway` is the compatibility floor. When Hermes adds a native feature, regenerating from
its OpenRPC document makes it visible without waiting for a new high-level REST wrapper. The
runtime contract also exposes `POST .../rpc` for dynamic callers and older generated clients.

## Dynamic tools

Tool bundles are attached to an instance, profile, or session. The SDK tool bridge presents the
bundle to Hermes as an MCP server. Hermes invokes a tool through the bridge, and the bridge calls
the consumer's `ToolCallRequest` handler. Session-scoped bindings should use an isolated
profile or process when strict cross-session isolation is required.

Hermes does not currently accept arbitrary tool definitions inside `prompt.submit`. Therefore a
`toolBindingId` on `SubmitTurnRequest` means “reconcile this binding first, then submit the native
prompt.” The adapter performs the corresponding native `mcp.servers.add`, `mcp.reload`, and
`tools.configure` flow. This keeps dynamic tools feasible without pretending the upstream prompt
method has a parameter that it does not have.

## Provisioning modes

The control plane supports logical and physical isolation:

- `external`: connect to an already-running Hermes endpoint.
- `process`: launch `hermes serve` with an isolated `HERMES_HOME`.
- `container`: launch a dedicated container.
- `kubernetes`: create or adopt Kubernetes workload resources.
- `nous_cloud`: provision lifecycle through the Nous Portal management surface.

## Kubernetes pool model

A Kubernetes pool is a homogeneous `StatefulSet` of Hermes containers. Each pod is one concrete,
addressable SDK instance with a stable ordinal, stable service DNS name, and its own `/opt/data`
PVC. Profiles live inside an instance; they are not Kubernetes replicas. Pool leasing selects an
instance and then a profile, returning both identifiers to the caller.

Use the official `nousresearch/hermes-agent` image as the upstream base. The reference derivative
in [`deploy/image/Dockerfile`](deploy/image/Dockerfile) runs `hermes serve` directly as UID 10000.
[`deploy/kubernetes/hermes-pool.yaml`](deploy/kubernetes/hermes-pool.yaml) supplies probes, isolated
storage, browser shared memory, resource bounds, stable networking and restricted ingress. See
[`deploy/kubernetes/README.md`](deploy/kubernetes/README.md) for the operational model.

Configuration is deliberately not encoded by producing one image per profile. The image contains
software; the per-instance PVC contains Hermes state; Kubernetes Secrets contain credentials; and
the SDK bootstrap contract creates profiles, MCP registrations and tool bindings. Build a derived
image only when a tool needs durable system packages or binaries.

## Programmatic per-user provisioning

The SDK supports both a reusable base image and images built on demand:

```text
image recipe
  -> isolated asynchronous build
  -> vulnerability/policy verification
  -> immutable OCI digest + SBOM + provenance
  -> user-owned instance
  -> user-owned profile
  -> capability discovery + connection descriptor
  -> runtime and native Hermes calls
```

Use `sdk.images.startImageBuild()` when image creation and instance creation are separate product
steps. Use `sdk.controlPlane.provisionUserInstance()` for the single-call workflow: it accepts
either a `managedImageId` or an inline build recipe, reuses an identical verified image when
allowed, creates the container or Kubernetes pod, bootstraps its profile and ultimately returns
the `instanceId`, `profileId`, and connection information.

Every recipe, build, image and instance carries `{tenantId, subjectId}` ownership. An image recipe
may install pinned APT, Python and Node packages and copy pre-uploaded artifacts. Build secrets are
ephemeral secret mounts; they are never Docker build arguments, environment layers or returned in
logs. Production policy should require an official digest-pinned Hermes base, a successful scan,
an SBOM, provenance, a signature and an immutable result digest before instance creation.

A complete request is available at
[`examples/provision-user-instance.request.json`](examples/provision-user-instance.request.json).
The recipe owner must match the provisioning-job owner; implementations reject cross-owner image
use unless an explicit image-sharing grant exists.

## Validation

The contracts use OpenAPI 3.1. Run the local structural check with:

```powershell
python scripts/validate_contracts.py
npx --yes @redocly/cli@latest lint "contracts/openapi/*.yaml"
```
