# Production control plane

This deployment is the real infrastructure implementation behind the SDK contracts. It does not
use the mock engine. It runs durable jobs in PostgreSQL, sends builds to a remote rootless BuildKit
daemon, scans and signs immutable images, and reconciles one isolated Kubernetes Deployment, PVC,
Service and credential Secret per Hermes instance.

## Required infrastructure

- Kubernetes 1.30 or newer with a default or explicitly configured `ReadWriteOnce` storage class.
- PostgreSQL 15 or newer reachable from `hermes-system`.
- An OCI registry and a `registry-auth` Docker config with push/pull permission.
- An OIDC issuer. Access tokens must carry `sub`, `tenant_id`, the configured audience and normal
  expiry/issued-at claims.
- A Cosign KMS key URI available through workload identity. Static private keys should not be
  stored in the repository.
- A DNS/TLS ingress or Gateway API route for the control-plane Service. Its internal URL must be
  placed in `EDITH_PUBLIC_BASE_URL` so runtime pods can reach callback-tool MCP endpoints.

## Images

The release workflow publishes:

```text
ghcr.io/anasmaar/edith-hermes-control-plane:<version>
ghcr.io/anasmaar/edith-hermes-runtime-bridge:<version>
ghcr.io/anasmaar/edith-hermes-mock:<version>
```

The runtime bridge is a sidecar beside every Hermes container. Hermes remains bound to pod
loopback; only the bridge is exposed through the internal Service. It translates the SDK's HTTP
RPC calls and SSE event streams to Hermes' native newline-delimited JSON-RPC WebSocket at
`/api/ws`.

## Configure and install

1. Copy `secrets.example.yaml` into your secret-management system. Do not apply the example
   values. Create `edith-hermes-control-plane-secrets`, `registry-auth`, and any referenced build
   or callback secrets.
2. Replace the OIDC issuer, public URL, registry names and pinned image digests in
   `production.yaml`.
3. Give the control-plane ServiceAccount the cloud workload identity needed by its Cosign KMS key
   and registry.
4. Apply the manifests:

```bash
kubectl apply -f deploy/control-plane/production.yaml
kubectl -n hermes-system rollout status statefulset/buildkit
kubectl -n hermes-system rollout status deployment/edith-hermes-control-plane
```

5. Confirm that unauthenticated access is rejected and authenticated readiness succeeds:

```bash
curl -i https://YOUR_CONTROL_PLANE/v1/instances
curl -H "Authorization: Bearer $EDITH_TOKEN" \
  https://YOUR_CONTROL_PLANE/health/ready
```

## Build security

Production recipes are restricted to configured base repositories and require a digest-pinned
base. BuildKit pushes by immutable digest and emits SBOM and SLSA provenance attestations. Trivy
rejects HIGH or CRITICAL vulnerabilities, and Cosign signs the resulting digest through the
configured KMS key. Build and callback secrets are mounted files; they are never Docker build
arguments or returned by the API.

## Failure and scaling behavior

Jobs are stored before workers accept them. Workers claim jobs with PostgreSQL row locks and
`SKIP LOCKED`, so multiple control-plane replicas cannot execute one queued job simultaneously.
Image and instance ownership is enforced from verified OIDC claims on every lookup. Kubernetes
resource names carry the SDK instance ID, and the provider uses create-or-patch reconciliation so
a retry converges instead of creating a second runtime.

BuildKit is a separate rootless StatefulSet with persistent cache. Scale control-plane replicas
independently; increase `EDITH_WORKER_CONCURRENCY` only after measuring BuildKit, registry and
cluster capacity.
