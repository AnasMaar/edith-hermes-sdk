# Local verification — 2026-09-23

Historical report. For current results, including successful real-model Python
tool calls, see [September 30 verification](verification-2026-09-30.md).

These are working-tree results on Windows with Docker Desktop, not claims about the
previously published v0.3.1 package. The original demo failed in the first real run.

## Verified against real Hermes

- Official image: `nousresearch/hermes-agent@sha256:c8a3377858895ea2329cd533f490e6f7b500e0a3611077712fe0df20661e3b78`.
- Docker provisioning and authenticated native WebSocket connections.
- Two native profiles, Adam and Anas, and a native session under each profile.
- Profile-specific MCP server registration. Native `mcp.servers.test` connected from
  Hermes inside Docker to each Python bridge and discovered the correct two tools.
- Adam's native configuration did not include Anas's server, and vice versa.
- A cross-profile SDK callback invocation was rejected (404).
- Direct SDK callback execution returned the demo weather and saved Anas's note.
  Weather is a fixed sample, not a live weather lookup.
- The new typed `Hermes` / `Agent` / `Model` / `@tool` interface created real Docker
  profiles, tool bindings and sessions and cleaned up its instances.
- Docker restart and reattachment preserved both profiles and their distinct MCP
  configurations; new native sessions were created after restart.
- Kubernetes v1.33.2 in a dedicated `kind-edith-sdk` cluster: real Deployment, PVC,
  Secret and Service; two ready containers (Hermes and bridge); two profiles and
  sessions; unauthenticated bridge request rejected; workload and PVC deleted.
  The smoke test uses a loopback port-forward from Windows. Production control
  planes normally reach the private Service from inside the cluster.
- 27 automated tests passed with unhandled-thread warnings treated as errors.
  SDK and service type checks, Ruff lint, contract validation, and package build passed.
  These include unit/fake tests and do not replace the separately listed live checks.

## Not yet verified / limitations

- A successful LLM-generated response/tool call has **not** been demonstrated.
  The installed Ollama `gemma3-tools:12b` model serves 4,096 context tokens. Native
  Hermes rejected it because it requires at least 64,000. This failure is surfaced
  as a failed turn, not a successful acknowledgement. No cloud key was supplied.
- The direct Python callback check is not proof that an LLM selected that tool.
- PostgreSQL, OIDC, KMS, remote registries, image-signing/scanning, cloud adapters,
  multi-node/replica operations and the entire native RPC catalog have not been
  exhaustively exercised here. Some existing higher-level adapters still need
  dedicated integration coverage; do not interpret this report as production certification.
- Profiles separate configuration and state, not OS security identities. Use one
  container/pod per mutually untrusted user. Shared-profile filesystem or terminal
  access is not a tenant security boundary.
- Native event replay is bounded. A restart/replay gap marks a pending SDK turn
  failed with an explicit history-unavailable error; inspect native session history.
- Python tools hosted by `Hermes.local` require its context/process to stay alive.
- No general-purpose application-table abstraction is introduced. Existing control
  plane metadata still uses SQLite or PostgreSQL. Your own tables/services can be
  used inside ordinary Python tool functions; Agno database compatibility is not claimed.

## Repeat the demonstrations (repository checkout)

```powershell
uv sync --extra control-plane
uv run python examples/docker_two_profiles.py --no-pause
uv run python examples/agents_docker.py
uv run python examples/agents_docker.py --restart
# Needs a supported, sufficiently sized model; existing local Gemma fails the 64K check:
uv run python examples/agents_docker.py --run
```

Local Kubernetes was installed using `.integration/kind.exe` v0.33.0, with kubeconfig
`.integration/kubeconfig`. The v1.37.0 default node did not boot on this Docker setup;
v1.33.2 did. No global kubeconfig/context was changed.

```powershell
docker build -f deploy/image/Dockerfile --build-arg HERMES_BASE_IMAGE=nousresearch/hermes-agent@sha256:c8a3377858895ea2329cd533f490e6f7b500e0a3611077712fe0df20661e3b78 -t edith-hermes:integration .
docker build -f services/runtime_bridge/Dockerfile -t edith-runtime-bridge:integration .
.integration/kind.exe load docker-image edith-hermes:integration edith-runtime-bridge:integration --name edith-sdk
$env:KUBECONFIG = (Resolve-Path .integration/kubeconfig).Path
# Created once during setup; it remains after demo cleanup:
# kubectl create namespace edith-demo
uv run python examples/kubernetes_smoke.py
```

The dedicated cluster and downloaded/built images remain for further testing.
The scripts remove their demo workloads. No Docker-wide prune is used.
Local state/credentials under `.demo/`, `.edith-hermes/`, and `.integration/` are ignored by Git.

## Interface design references

The convenience layer follows the compositional style in Agno's
[SDK introduction](https://docs.agno.com/sdk/introduction) and
[dependency injection examples](https://docs.agno.com/dependencies/agent/overview).
Agno's [SQLite table configuration](https://docs.agno.com/database/providers/sqlite/usage/sqlite-for-agent)
is distinct from runtime provisioning; we do not require its database or copy its
storage schema into Hermes. The original generated 64 HTTP operations and 219
pinned native RPC methods remain accessible through `hermes.sdk` and `agent.rpc(...)`.
