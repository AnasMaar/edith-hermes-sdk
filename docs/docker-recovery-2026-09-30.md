# Docker recovery and persistent RPC verification — 2026-09-30

Source version remains **0.4.0**. This supplements the
[earlier verification report](verification-2026-09-30.md); earlier failures remain
historical evidence, not retroactively successful runs.

## Host recovery

Docker Desktop's startup log identified a stale, inaccessible telemetry socket:
`run/userAnalyticsOtlpHttp.sock`. With the backend stopped, its runtime-socket
directory was renamed to the recoverable
`run.edith-backup-20260930-1251` under the user's local Docker directory. Desktop
then started successfully, with Docker Engine 28.0.4 and the existing single-node
kind Kubernetes 1.33.2 cluster Ready.

The previous failed-test container
`edith-hermes-instance-e275893a827b4fcab7022dd1ad2e8f04` and its verified, matching
test-data volume were removed. That disposable test data was deleted; user
volumes, images, the cluster and the Ubuntu distribution were preserved. No
factory reset, Docker-wide prune, pagefile change or user-file cleanup was used.

## Actual bug found and fixed

The default progressive-search repeat initially called the multiplication tool,
then its next turn failed with native `session not found`. The control plane and
HTTP runtime bridge opened and closed a native WebSocket for each RPC. Hermes
owns sessions on that connection and reaps detached sessions after its orphan
grace period (20 seconds in the tested implementation).

Both services now retain their RPC connection until shutdown or instance
deletion. A small shared internal `edith_hermes_rpc` package correlates concurrent
calls with unique wire IDs and continuously drains notifications. This does not
change the public SDK interface or add mandatory dependencies to the base SDK.

- Native results/error codes, including false results, are preserved.
- Timeout and cancellation clear pending calls without misrouting late replies.
- An ambiguous write is never automatically replayed. A subsequent new call can
  reconnect; a detached native session may still need explicit resume.
- Interactive server requests require the existing explicit duplex API. This
  RPC-only channel does not silently approve or answer them.
- Credential changes create a separate authenticated connection/cookie jar.
- Failed/cancelled handshakes and service shutdown close their owned sockets;
  runtime deletion forgets cached connections.

## Measured checks

| Check | Result |
| --- | --- |
| Windows Python 3.10–3.13 | 378 tests passed on each version; includes 18 new regressions/preflight cases |
| Quality | Ruff, strict SDK/shared-transport and service mypy, contract validator and Redocly passed |
| Packaging | Source/wheel builds; isolated wheel-only installation imports the SDK, shared transport and control plane; transport `py.typed` and 64 HTTP / 219 native RPC mappings verified |
| Control-plane image | Rebuilt; default UID-10000 SQLite write/startup/readiness passed |
| Docker / real Hermes | Adam/Anas profiles, profile-scoped MCP discovery, config readback, session activate/branch/close/resume/delete, persistent duplex, native profile clone/delete and cleanup passed with a configured local model |
| Real direct-schema tools after connection fix | Observed multiplication callback returned 96; after a 25-second idle gap, dynamically attached addition callback returned 42 in the same session; other profile unchanged; removal and cleanup passed |
| Kubernetes / rebuilt bridge | Two profiles, three sessions, unauthenticated RPC rejected, authenticated RPC and duplex passed; both HTTP-created native sessions remained active after 25 seconds; owned Deployment/Service/Secret/PVC removed |
| Process / real Hermes | Repeated in a disposable official Linux container: authenticated RPC, session creation, stop/start profile persistence and cleanup passed; not native Windows process certification |
| PostgreSQL 16 | Repeated disposable-container CRUD/owner isolation, reconnect persistence, eight-worker job/lease exclusivity, expiry and stale-release protection passed |

The tested bridge image was `edith-runtime-bridge:recovery-20260930`, local image
ID `sha256:bf8f434ef691b61544216aa9129629997b7868c15b46ad31ea9d2e174e9f4163`.
The tested control-plane image was `edith-control-plane:recovery-20260930`, local
image ID `sha256:094ba835e14a973cc403ad1c8d72de939830efa9d45fdb2c6fc17d3a88d040d8`.
These are local test builds, not registry releases.

## Failures and host limits retained

An initial Docker lifecycle run without any native model/provider configured
could not activate/branch a session. Repeating with the installed local model
passed; these native actions require agent construction/provider configuration.

The final progressive-search model repeat was **aborted for low host disk
space**, not passed. The 64K local model again drove C: below 1 GiB free. Its
temporary alias was removed and its verified test runner stopped to prevent
further retries/reloads; subsequent native turns consequently reported model
unavailable/404. Owned instance and binding cleanup nevertheless passed. No
cloud model key or paid fallback was selected, and original model weights remain.

After unload/cleanup, C: had approximately 10 GiB free, Docker was running and
Kubernetes Ready. That is insufficient headroom for another comparable model
repeat. The live script now defaults to a conservative **16 GiB initial
temp/state-drive reserve** for model tests, checked before creating a workload.
`--min-free-gb` can explicitly adjust it for a different test environment; a
preflight threshold does not guarantee capacity throughout generation. The SDK
itself does not impose this demo-only disk requirement.

The final progressive callback repeat therefore remains unverified after this
fix. Earlier successful progressive callbacks and the earlier model's missed-tool
result remain recorded separately. The RPC session-retention defect is covered
by the successful real direct-schema and Kubernetes idle-gap checks; these do
not certify deterministic tool discovery for every model.

## Reproduction and boundaries

```powershell
uv sync --frozen --all-extras --group dev
uv run pytest
uv run mypy src/edith_hermes src/edith_hermes_rpc
uv run mypy --ignore-missing-imports services/control_plane/edith_hermes_control_plane services/runtime_bridge/edith_hermes_runtime_bridge
uv run python scripts/validate_contracts.py
uv run python scripts/verify_postgres_live.py
# With adequate disk/RAM and a local 64K tool-capable model:
uv run python scripts/verify_live.py --model YOUR_MODEL --direct-tools --idle-gap 25
uv run python scripts/verify_live.py --model YOUR_MODEL --idle-gap 25
# With a scoped kubeconfig and locally loaded runtime/bridge images:
uv run python scripts/verify_kubernetes_live.py --bridge-image YOUR_BUILT_BRIDGE_IMAGE --idle-gap 25
```

The Kubernetes script uses the existing test namespace/runtime image; it does
not install or reset a cluster. Process verification needs Hermes installed in
Linux. All other infrastructure/feature limitations in the earlier report still
apply, including production failover, external OAuth/OIDC/KMS and native RPCs not
executed live. Use one bridge worker per native runtime, and stable per-instance
routing for direct-WebSocket control-plane workers; SQL job locks do not replace
native connection/session ownership. Build the bridge from this checkout before
using the persistent HTTP RPC behavior.
