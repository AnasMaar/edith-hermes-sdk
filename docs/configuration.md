# Composable control-plane configuration

The Python SDK does not require PostgreSQL, OIDC, KMS or Kubernetes. Those are independent
deployment choices. `Settings` can be constructed directly for an embedded control plane or
loaded from equivalent `EDITH_*` environment variables for the FastAPI service.

## Minimal local control plane

```python
from edith_hermes_control_plane.config import Settings

settings = Settings(
    database_url="sqlite+aiosqlite:///./edith-hermes.db",
    auth_mode="none",
    enabled_runtime_providers=["external", "process", "container"],
    require_digest_pinned_base=False,
    require_image_scan=False,
    require_image_signature=False,
)
```

This topology has one durable SQLite file, no bearer-token requirement, no KMS operation and no
cluster dependency. The container provider talks to the Docker-compatible API selected by the
normal Docker environment (`DOCKER_HOST`, contexts and credential helpers). The process provider
executes `hermes serve` and gives each instance its own `HERMES_HOME`.

## Runtime providers

Set `EDITH_RUNTIME_PROVIDERS` to a comma-separated subset of:

| Kind | Required request fields | Lifecycle ownership |
| --- | --- | --- |
| `external` | `runtime.endpoint` pointing to a bridge HTTP URL or native WebSocket | Adopt only; external supervisor owns the process |
| `process` | Optional `executable`, `command`, `hermesHome` | Starts and terminates a local child process |
| `container` | `image` or `managedImageId` | Creates, starts, stops and removes a Docker-compatible container and volume |
| `kubernetes` | `image` or `managedImageId`; optional placement | Reconciles a Deployment, Service, Secret and PVC |
| `nous_cloud` | Adapter-specific `runtime.cloud` values | Delegates provision/scale/delete to `EDITH_CLOUD_INVOKE_URL` |

The runtime provider is stored in each instance's `runtimeIdentity`, so later lifecycle calls are
routed back to the same provider. Pools preserve the provider declared by their template.

## State backends

- `sqlite+aiosqlite:///./file.db` is the default and is appropriate for one control-plane process.
- `sqlite+aiosqlite:///:memory:` is useful for ephemeral tests.
- `postgresql+asyncpg://...` supports durable jobs shared safely by multiple API/worker replicas.

All backends store resources, jobs, logs, ownership, leases and idempotency records through the
same SQLAlchemy repository. PostgreSQL is only needed for multi-replica job claiming; it is not
part of a Hermes instance.

SQLite queues access through one connection per database object and uses WAL;
keep it on a local filesystem. Atomic job and lease claims are tested on both
databases. This is not general multi-writer pool reconciliation or crash-recovery
certification; use one controller for pool resizing/deletion.

## Authentication modes

| `EDITH_AUTH_MODE` | Behavior |
| --- | --- |
| `none` | No `Authorization` header. Uses `EDITH_ANONYMOUS_TENANT_ID` and `EDITH_ANONYMOUS_SUBJECT_ID`, optionally overridden by `X-Edith-Tenant` and `X-Edith-Subject`. |
| `static` | Bearer tokens resolve through the JSON `EDITH_DEV_TOKENS` map. Useful for private/local services. |
| `oidc` | JWT signature, issuer, audience, time claims, tenant claim and subject claim are validated through JWKS. |

The Python remote client accepts `token=None`, so the same generated methods work in every mode.

## Image policy

The following controls are independent:

- `EDITH_REQUIRE_DIGEST_PINNED_BASE`
- `EDITH_REQUIRE_IMAGE_SCAN`
- `EDITH_REQUIRE_IMAGE_SIGNATURE`

When signing is disabled, no Cosign key or KMS exists in the request path. When enabled,
`EDITH_COSIGN_KEY` may be any key URI supported by Cosign, including a local key, hardware-backed
key or cloud KMS URI. Building images is optional: container and Kubernetes requests can use a
direct `runtime.image`, while external and process runtimes need no image.

Local process/container `environment.secretRef` values resolve through
`EDITH_SECRET_PROVIDER=environment` (`EDITH_SECRET_<NAME>_<KEY>`) or
`EDITH_SECRET_PROVIDER=files` (`EDITH_SECRET_DIRECTORY/<name>/<key>`). Kubernetes secret
references remain native Kubernetes `Secret` references.

## Hardened Kubernetes profile

For the 0.4.0 duplex protocol, build the bridge from this checkout and explicitly
set `EDITH_RUNTIME_BRIDGE_IMAGE` to that image/digest. Existing v0.3.1 image tags
in the reference deployment are older releases, not automatically updated by a
source push.

[`deploy/control-plane/production.yaml`](../deploy/control-plane/production.yaml) explicitly opts
into PostgreSQL, OIDC, Kubernetes, digest pinning, Trivy and Cosign/KMS. It is one deployment
profile, not an SDK requirement.

## Native connection ownership

The control plane retains one authenticated RPC WebSocket per native connection
descriptor; the HTTP runtime bridge retains one per application worker. Hermes
owns native sessions on those sockets. Keep one bridge worker per runtime and
route direct-WebSocket instances to a stable control-plane worker. PostgreSQL
job locks alone do not provide distributed native session ownership or failover.
After a connection loss, a new call reconnects without replaying the interrupted
command; resuming the native session may still be required. Interactive server
requests use the explicit duplex API, not the RPC-only connection.
