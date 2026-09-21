# EDITH Hermes SDK

`edith-hermes-sdk` is the Python control surface for building, provisioning, and operating
user-owned Hermes runtimes. It supports a remote control plane and an in-process control plane
through the same API. Version 0.3 makes infrastructure policy composable: SQLite or PostgreSQL;
anonymous, static-token or OIDC authentication; optional scanning and signing; and external,
process, Docker-compatible container, Kubernetes or adapter-backed cloud runtimes.

## Install and use

```bash
uv add "edith-hermes-sdk[control-plane]"
```

```python
from edith_hermes import AsyncEdithHermes

async with AsyncEdithHermes.remote(
    base_url="http://localhost:8080",
    token="dev-user-1",  # omit this when the deployment uses auth_mode="none"
) as sdk:
    instances = await sdk.control_plane.list_instances()
```

The SDK can also host the real control plane inside the calling Python process—without
PostgreSQL, OIDC, KMS or Kubernetes:

```python
from edith_hermes import AsyncEdithHermes
from edith_hermes_control_plane.config import Settings

settings = Settings(
    database_url="sqlite+aiosqlite:///./hermes.db",
    auth_mode="none",
    enabled_runtime_providers=["container"],  # Docker/Podman-compatible API
)

async with await AsyncEdithHermes.local(settings=settings) as sdk:
    capabilities = await sdk.control_plane.get_control_plane_capabilities()
    job = await sdk.control_plane.provision_user_instance(
        body={
            "owner": {"tenantId": "local", "subjectId": "local-user"},
            "name": "my-hermes",
            "runtime": {
                "kind": "container",
                "image": "nousresearch/hermes-agent:latest",
            },
            "bootstrap": {"profile": {"name": "default"}},
        }
    )
    ready = await sdk.wait_for_provisioning_job(job["id"])
```

See [`docs/configuration.md`](docs/configuration.md) for all provider combinations.

For a complete local demonstration, run
[`examples/docker_two_profiles.py`](examples/docker_two_profiles.py). It creates one real Hermes
container, isolated `Adam` and `Anas` profiles, separate sessions, and profile-scoped callback tool
bundles, then executes one tool from each bundle.

Start the persistent mock server with:

```bash
docker compose -f deploy/compose.yaml up --build
```

The default development identities are `dev-user-1` and `dev-user-2`. Override
`EDITH_MOCK_TOKENS` with a JSON token-to-owner map outside local development.

Deploy the real control plane using
[`deploy/control-plane/README.md`](deploy/control-plane/README.md). The mock image is for local
contract tests only and is never used by the production deployment.

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
sdk.control_plane    generated from control-plane.openapi.yaml
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

These modes are implemented by a runtime-provider registry. Instance updates, start/stop/restart,
deletion, pool scaling and provisioning all route through the provider recorded in
`runtimeIdentity`; none of those paths assumes Kubernetes.

| Concern | Lightweight choice | Scale-out/hardened choice |
| --- | --- | --- |
| State | SQLite file or SQLite memory database | PostgreSQL |
| Authentication | None | Static bearer or OIDC/JWKS |
| Runtime | Existing endpoint, local process, local container | Kubernetes or cloud adapter |
| Image scan | Disabled | Trivy |
| Image signature | Disabled | Cosign with a file key, hardware key or KMS URI |

`GET /v1/system/capabilities` (and
`sdk.control_plane.get_control_plane_capabilities()`) reports the effective non-secret selection.

## Kubernetes pool model

The generic control-plane pool creates one independently addressable runtime per desired member.
With the Kubernetes provider, each member is currently a dedicated `Deployment`, Service, Secret
and `/opt/data` PVC. The separate static Kubernetes blueprint demonstrates a homogeneous
`StatefulSet` topology for operators who prefer stable ordinals. Profiles live inside an instance;
they are not Kubernetes replicas. Pool leasing selects an instance and then a profile.

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

Use `sdk.images.start_image_build()` when image creation and instance creation are separate product
steps. Use `sdk.control_plane.provision_user_instance()` for the single-call workflow: it accepts
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
