# Hermes Kubernetes runtime pool

This reference deployment models a pool as a Kubernetes `StatefulSet`:

```text
SDK pool
└── StatefulSet/hermes-pool
    ├── hermes-pool-0  -> SDK instance -> /opt/data PVC -> profiles
    ├── hermes-pool-1  -> SDK instance -> /opt/data PVC -> profiles
    └── hermes-pool-2  -> SDK instance -> /opt/data PVC -> profiles
```

One pod is one SDK-addressable Hermes instance. A profile remains a Hermes-native isolated home
inside that instance. The stable instance address is:

```text
hermes-pool-<ordinal>.hermes-pool-headless.<namespace>.svc:9119
```

The SDK control plane owns `StatefulSet.spec.replicas`, readiness, lease assignment, draining and
profile bootstrap. Do not attach an HPA to the same StatefulSet: two independent reconcilers must
not both write the replica count. An autoscaler should instead update the SDK pool's `desiredSize`.

## Image

Nous Research publishes `nousresearch/hermes-agent` for `linux/amd64` and `linux/arm64`. The
upstream image uses `/opt/data` as durable `HERMES_HOME`, runs Hermes as UID 10000 after its Docker
initialization, and contains the web backend and browser dependencies. `deploy/image/Dockerfile`
derives from it but runs a single `hermes serve` process directly as UID 10000, which fits the
Kubernetes one-process-per-container model and the Restricted Pod Security profile.

Build and push an immutable image:

```bash
docker build \
  --build-arg HERMES_BASE_IMAGE=nousresearch/hermes-agent:<release-or-digest> \
  -t registry.example.com/hermes-sdk-runtime:0.1.0 \
  -f deploy/image/Dockerfile .
docker push registry.example.com/hermes-sdk-runtime:0.1.0
```

Replace `hermes-sdk-runtime:dev` in the StatefulSet with the pushed digest. Do not deploy
`:latest` to a production pool: every instance in a rollout must report the same image digest and
Hermes contract revision.

## Configuration and secrets

Create `hermes-runtime-env` through your secret manager or, for a development cluster, with:

```bash
kubectl -n hermes-runtimes create secret generic hermes-runtime-env \
  --from-literal=HERMES_DASHBOARD_BASIC_AUTH_USERNAME=sdk-control-plane \
  --from-literal=HERMES_DASHBOARD_BASIC_AUTH_PASSWORD='<strong-development-password>' \
  --from-literal=HERMES_DASHBOARD_BASIC_AUTH_SECRET='<32-or-more-random-bytes>' \
  --from-literal=OPENROUTER_API_KEY='<provider-key>'
```

Prefer `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` over the plaintext password. For an
internet-reachable backend, use Nous OAuth or your OIDC provider instead of basic authentication.
The reference Service is headless and the NetworkPolicy only permits the SDK control plane in the
`hermes-system` namespace; it does not create an Ingress or public LoadBalancer.

Profiles, MCP registrations and user state are not baked into the image. The control plane writes
their bootstrap data into that instance's PVC using the Hermes gateway interfaces. A different
derived image is justified only when a tool needs an OS package or binary available immediately at
boot. Network services and heavyweight tool servers should normally be sidecars or separate MCP
workloads.

## Apply

After creating the namespace, secret and image pull credentials:

```bash
kubectl -n hermes-runtimes apply -f deploy/kubernetes/hermes-pool.yaml
kubectl -n hermes-runtimes rollout status statefulset/hermes-pool
```

Label the control-plane namespace as expected by the NetworkPolicy:

```bash
kubectl label namespace hermes-system kubernetes.io/metadata.name=hermes-system --overwrite
```

