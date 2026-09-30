# Verification pass — 2026-09-25

Historical report. The subsequent [September 30 pass](verification-2026-09-30.md)
resolved the model/tool execution failure and added regression/live coverage.

This describes the unreleased working tree, not the published 0.3.1 package.
It does not certify every RPC or every infrastructure provider for production.

## Implemented fixes with regression coverage

| Area | What was tested | Evidence level |
| --- | --- | --- |
| Generated typing | `allOf` no longer discards base fields; MCP and tool-bundle arguments and required keys are retained | Generator/typing tests |
| Profiles | Config uses native config commands; soul/description/model/provider use native configure; failed native deletion preserves registry entry | Real HTTP + SQLite; contract-checking native double |
| Sessions | Working-directory mapping, resume, branch, close, activate, interrupt, undo, stored/live ID distinction, cross-profile rejection | Real HTTP + SQLite; contract-checking native double |
| Turns | Structured content preserved, enqueue flag mapped, resumed native ID used, stop/steer/approval routing | Regression tests with native double |
| MCP bindings | Correct native config nesting, environment mapping, scoped filtering and native unregistration | Real HTTP + SQLite; contract-checking native double |
| MCP OAuth | Native test/start/callback/poll/cancel forwarding, flow IDs, explicit target selection | Simulated native OAuth responses; no provider login |
| Persistent WebSockets | In-process and remote clients, authentication rejection, forced profile routing, concurrent calls, server-request replies, duplicate-answer rejection, disconnect cleanup | Real loopback TCP/WebSocket servers; simulated native gateway |
| Runtime bridge | Full bidirectional forwarding under bearer authentication, including same-connection server-request replies | Real loopback TCP/WebSocket bridge; simulated native gateway |

Full test suite: **338 passed**. Tests include older unit/fake tests and the new
HTTP/SQLite/TCP integration tests. Test counts are not evidence of real-model reasoning.

## Live verification completed in the follow-up pass

- Docker Desktop was recovered without a factory reset. Its backend was failing
  while removing an inaccessible stale telemetry socket. After stopping Docker,
  its runtime socket directory was moved to the recoverable sibling
  `C:\Users\ultrapc\AppData\Local\Docker\run.edith-backup-20260925` and Docker
  restarted. Existing images, volumes and the kind cluster were preserved.
- **Docker / actual Hermes:** `examples/agents_docker.py --restart` passed two
  profiles, sessions, MCP setup, restart/reattach and cleanup. `scripts/verify_live.py`
  additionally passed native MCP discovery and profile separation, config readback,
  seeded session branch/activate/close/resume/delete, persistent RPC, native profile
  clone/delete, binding removal and cleanup.
- **Kubernetes / actual Hermes:** `scripts/verify_kubernetes_live.py` passed against
  the existing single-node `edith-sdk` kind cluster. It created two profiles and
  three sessions, rejected an unauthenticated bridge request, exercised persistent
  authenticated WebSocket RPC, and removed its Deployment, Service, Secret and PVC.
  The bridge was rebuilt from the current source as
  `edith-runtime-bridge:verification-20260925` and loaded into kind.
- **Process / actual Hermes:** `scripts/verify_process_live.py` passed authenticated
  RPC, session creation and stop/start persistence inside a disposable Linux
  container using the real Hermes executable. This does **not** verify Windows-native
  Hermes installation. Process startup now generates a bearer token and directs
  stdout to a log file instead of an undrained pipe; failed startup clears its registry.
- **PostgreSQL 16:** `scripts/verify_postgres_live.py` passed schema creation,
  resource CRUD, owner isolation, persistence across database-client reconnect,
  and exclusive job claiming by eight concurrent workers. PostgreSQL ran in a
  disposable localhost-only container with temporary storage. This is a storage
  integration test, not a multi-node control-plane or crash-recovery certification.
- **Quality:** Ruff, SDK/service mypy, contract validation, deterministic regeneration
  (64 HTTP operations / 219 RPC methods), and source/wheel packaging passed.
  Generation coverage does not mean every native method was invoked live.

## Real model failure and remaining unverified integrations

- **Actual local tool execution failed.** Installed `gemma3-tools:12b` produced
  text representing a tool call but did not invoke the Python callback. Native MCP
  discovery correctly returned `verification_multiply`; that alone is not execution.
  A profile context override still resulted in Ollama serving 4K, so the test was
  repeated using a temporary alias configured and observed at 64K. That attempt
  returned a fenced `tool_call` and `96`, but the observed callback list was empty.
  The test correctly failed. No successful end-to-end model-selected tool call is
  claimed, and the exact model/template/serving cause is not yet established.
  The alias was removed afterward; the original model was unchanged.
- No OAuth-protected test MCP server or cloud-adapter deployment/credentials were
  supplied. OAuth forwarding tests do not prove a successful provider consent flow.
- External registry, scanning/signing, external OIDC/KMS and multi-node testing
  remain separate integration work, not validated by the default SQLite suite.

## Still not implemented (now rejected where previously ignored)

- Per-turn and per-session tool isolation, and instance-wide automatic tool
  registration. Use separate profile-level bindings; do not treat profiles as
  security isolation between untrusted users.
- Per-session environment overrides.
- Branching by SDK `fromTurnId`. Native `session.branch(count=...)` remains
  accessible, but an SDK turn ID is not interchangeable with a native message count.
- MCP secret-reference and native allow-list reconciliation; callback bundle
  filtering and native profile credential configuration are separate alternatives.
- Complete typed cloud-management coverage still needs an authoritative provider
  contract and a concrete adapter. No cloud APIs were invented to fill this gap.

Raw native APIs remain available, but invoking raw methods is not a substitute for
the missing high-level isolation semantics. These limitations prevent a claim that
"every use case works". The remaining model/tool failure, unsupported semantics
and external-provider checks must not be hidden behind the passing test count.

No existing user workloads, profiles, or volumes were deleted by these tests.
Test-owned runtime workloads, temporary data and the temporary Ollama model alias
were deleted; those disposable test resources are not recoverable. Existing model
weights, the kind cluster, cached images, the new bridge image, and the recoverable
Docker socket backup remain. Docker Desktop is now running. Nothing was published.
