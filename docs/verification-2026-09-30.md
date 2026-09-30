# Verification and stabilization — 2026-09-30

Source version **0.4.0**. These are measured local results, not certification of
every Hermes feature, model, cloud integration or production topology.

## Quality gates

- **360 tests passed on each of Python 3.10, 3.11, 3.12 and 3.13** on Windows,
  including the final cleanup-failure regression.
- **360 tests also passed on each of Python 3.10–3.13 in Linux CI**. The earlier
  container-local Linux/Python 3.13 run passed 359 tests before the final cleanup
  regression was added.
- Ruff, SDK and service mypy, deterministic SDK regeneration, the repository
  contract validator and Redocly validation passed.
- Source/wheel builds passed. A clean wheel-only installation verified imports,
  version, `py.typed`, and all **64 HTTP / 219 native RPC** resource mappings.
- The control-plane, mock and runtime-bridge Dockerfiles built locally.
  These are test images, not newly published release images.
- All nine jobs passed in the [pre-promotion CI run](https://github.com/AnasMaar/edith-hermes-sdk/actions/runs/36657250404)
  and the [main-branch CI run](https://github.com/AnasMaar/edith-hermes-sdk/actions/runs/36657416575),
  including clean Linux image builds, default UID-10000 SQLite startup/readiness,
  the four-version test matrix, quality gates and actual PostgreSQL concurrency.

The tests include contract doubles and real HTTP/SQLite/TCP/WebSocket integration
checks. Native catalog coverage means correct typed dispatch and routing; it does
not mean all 219 RPCs were executed against an actual Hermes instance.

## Real infrastructure and model checks

| Check | Observed result |
| --- | --- |
| Docker / actual Hermes | Two profiles, scoped MCP discovery, config readback, seeded session activate/branch/close/resume/delete, persistent native RPC, native profile clone/delete, binding removal and owned-workload cleanup |
| Real Python tool selection | Local installed `gpt-oss:20b` called `verification_multiply(12, 8)` through Docker Hermes; the observed callback returned 96 |
| Dynamic tool attachment | The same model/session invoked a newly attached `verification_add(19, 23)` callback, returned 42, and the binding was removed without changing the other profile |
| Kubernetes / actual Hermes | Existing single-node kind v1.33.2 cluster; two profiles, three sessions, unauthenticated bridge rejection, authenticated persistent RPC, deletion of the test Deployment/Service/Secret/PVC |
| Process / actual Hermes | Disposable Linux container with real Hermes executable; authenticated RPC, session creation, stop/start profile persistence and cleanup; not Windows-native Hermes installation |
| PostgreSQL 16 | Disposable localhost-only container; schema/CRUD, owner isolation, reconnect persistence, exclusive job claim by eight workers, exclusive lease claim/expiry and protection from stale lease release |

The model was served through a temporary local Ollama alias with `num_ctx=65536`
and temperature zero. Direct MCP schemas and Hermes's default progressive tool
search both successfully invoked callbacks. No cloud model key or paid provider
was selected, and original model weights/configuration were not changed.
Ollama's OpenAI-compatible endpoint needs its serving context configured on the
model; a request/profile override alone is not a substitute. See the official
[OpenAI compatibility documentation](https://docs.ollama.com/api/openai-compatibility).

A clean-start repeat successfully called the initial tool but did **not** invoke
the dynamically added tool with the shorter discovery prompt. That failure is
retained as evidence: dynamic progressive-search execution is not deterministic
with this local model, and native reload can retain a name-identical bridge
schema's old listing. The repeat script now explicitly asks the model to discover
new deferred tools. For small tool collections, use profile
`config={"tool_search.enabled": "off"}` to expose the actual schemas directly.
Successful callback observation, not final answer text alone, is the test gate.

The final progressive-search repeat passed the initial callback, then failed
while persisting the dynamic turn because the host C: drive reached zero free
bytes (`sqlite3.OperationalError: database or disk is full`). Cleanup subsequently
timed out against Docker. A temporary kind image export/import and an additional
non-root image check were interrupted after Docker/WSL stopped responding. These
are **failed/incomplete repeats**, not additional successful live evidence. No
Docker-wide cleanup or deletion of user files was used to work around the issue.
The direct-schema clean-start repeat and earlier live checks above passed before
disk exhaustion. CI independently builds/tests the images in a clean Linux host.

## Bugs fixed, with regression coverage

- **Lazy session tool snapshots:** both native create and activate can leave the
  agent unbuilt. Before the first bound-tool prompt, a read-only native
  `process.list` waits for construction, then `reload.mcp(confirm=True)` discovers
  the profile's servers and refreshes its live tool snapshot. A session/binding
  revision avoids repeating discovery when bindings have not changed. Explicit
  reload confirmation does not disable native approval policy.
- **Truncated, undiscoverable tool names:** full UUID binding names consumed the
  native 64-character function-name budget. New bindings use short deterministic
  server names; old bindings retain their original registration names for
  deletion/OAuth compatibility. Tool search can now find common Python names.
- **Failure cleanup:** failed tool registration removes its pending registry row,
  callback and owned bundle. Runtime deletion cascades owned profiles, sessions,
  turns, bindings and leases while preserving other owners and reusable catalogs.
  Failed attachment after convenience provisioning cleans up the new runtime.
  Local-context exit attempts all owned instance deletions even if one fails,
  closes its callback/client resources, and surfaces the cleanup failure.
- **Lease allocation:** durable atomic reservations prevent concurrent callers
  from leasing one instance twice. Expired reservations use version-checked
  replacement; stale release cannot clear a newer lease. Pool/profile ownership,
  labels, size limits, leased-runtime protection and round-robin reuse are tested.
- **SQLite concurrency:** WAL, a queued single connection per database object and
  explicit write locking for claims avoid the lock failures exposed by concurrent
  HTTP requests and the Python-version test runs.
- **Convenience configuration/lifecycle:** direct config, `max_turns`, `toolsets`,
  ordinary annotated functions, `open_session`, `add_tools`, and `remove_tools`;
  validation before provisioning; serialized bound-agent operations; no mutation
  of caller-supplied local settings; loopback callbacks for process runtimes.
- **Non-root container defaults:** the control-plane image stores its default
  SQLite database, process runtime data and local secret directory under writable
  `/var/lib/edith`, rather than the root-owned application directory. CI checks
  startup/readiness and writes as UID 10000; persist that directory with a volume
  or select an external database explicitly.
- Earlier fixes for native IDs, profile config/deletion, OAuth forwarding,
  duplex replies and process/container startup remain covered; see the
  [historical September 25 report](verification-2026-09-25.md).

## Explicit boundaries

- Per-turn/session tool isolation, per-session environment overrides, automatic
  instance-wide tool registration, SDK `fromTurnId` branching, and MCP secret-ref
  or native allow-list reconciliation are still unsupported and rejected.
- Pools currently manage independent runtimes, not the reference StatefulSet.
  StatefulSet mapping, custom schedulers and automatic idle-TTL eviction are
  rejected. Serialize resizing/deletion through one controller; atomic lease/job
  claims do not certify concurrent pool reconcilers or general crash recovery.
  Least-session/busy ordering uses registry snapshots, not measured pod CPU load.
- External OAuth consent, OIDC/JWKS integration, KMS, registry publication,
  scanning/signing, cloud-adapter deployments, multi-node/replica failover and
  every native administrative RPC require separate infrastructure-specific tests.
- Python callback registries are process-local. Keep their host alive and use
  sticky routing/shared registration when deploying multiple callback workers.
- Profiles separate configuration/state, **not OS security identities**. Use one
  container/pod per mutually untrusted user. Anonymous control planes share a
  configured identity and must not be exposed as a multi-tenant public service.
- Build and select a bridge image from this checkout for the new duplex protocol.
  The v0.3.1 deployment examples are not proof that older images contain 0.4.0 code.
- Source version 0.4.0 is not a claim that a new PyPI release, GHCR image or release
  tag has been published. The existing package names and compatibility clients
  remain unchanged.

## Reproduction

```powershell
uv sync --all-extras --group dev
uv run pytest
uv run ruff check .
uv run mypy src/edith_hermes
uv run mypy --ignore-missing-imports services/control_plane/edith_hermes_control_plane services/runtime_bridge/edith_hermes_runtime_bridge
uv run python scripts/validate_contracts.py
uv run python scripts/verify_live.py --model YOUR_INSTALLED_64K_TOOL_CAPABLE_MODEL
uv run python scripts/verify_live.py --model YOUR_INSTALLED_64K_TOOL_CAPABLE_MODEL --direct-tools
uv run python scripts/verify_postgres_live.py
# Set a scoped kubeconfig and load the test runtime/bridge images first:
uv run python scripts/verify_kubernetes_live.py --bridge-image YOUR_BUILT_BRIDGE_IMAGE
```

`verify_process_live.py` must run in a Linux environment with Hermes installed at
its documented executable path. Test scripts remove only their owned workloads.
The kind cluster, cached images and recoverable Docker socket-directory backup
remain. One test container from the disk-full repeat may require cleanup after
Docker recovers; it is named
`edith-hermes-instance-e275893a827b4fcab7022dd1ad2e8f04`. The deletion request timed
out rather than being reported as successful. Scoped Docker Desktop/WSL restart
attempts did not restore the local engine: Desktop's backend reported
`context canceled`. Ubuntu was not terminated or globally restarted. Local
Docker recovery and that test container's cleanup remain separate host tasks;
the interrupted live repeat is not marked passed by the green CI run.
No Docker-wide prune, factory reset
or existing-user workload deletion was used. The temporary Ollama alias was
unloaded and removed; the original installed models remain. Tests and source
publication are separate steps.
