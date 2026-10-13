# Product-owned desktop extension bindings

`AsyncHermesExtensions(connection, profile="family-edith")` provides explicit
bindings for EDITH's versioned `edith.desktop.v1.*` RPC namespace. These are
separate from native Hermes RPC/REST methods and require the EDITH host extension.
Check `capabilities()` on the running deployment before enabling controls.

Current bindings support per-server MCP revisions, `update_mcp` and
`mcp_operation`. Each save carries the owning profile, server name, expected
revision, dirty-field patch and a durable request ID. Environment/header maps
merge supplied keys; explicit clear-key lists remove named entries. Unrelated
server fields and other profile settings remain backend-owned. Never reconstruct
configuration from a redacted inventory or retry an uncertain save automatically.

The extension serializes with native configuration locks and keeps a secret-free
operation journal. If a save succeeds but its reply is lost, reconciliation can
confirm the stored server fingerprint without replaying the mutation. Independent
CLI processes do not share the server's in-process lock; this binding does not
claim a cross-process filesystem transaction.

`git_inspect(path)` reads repository identity, common directory, HEAD, status and
branches on the owning host using Hermes's native Git helpers. Its versioned
extension capability is `git.inspect`; no shell or arbitrary command API is
exposed. Native Desktop `git.file_diff(path, file)` reads the complete difference
against HEAD, including both staged and unstaged changes.

`git_objects(path, requests, limit=4194304)` reads bounded blob/workspace bytes for
full diff expansion. Objects use hexadecimal blob IDs; disk reads stay within
the repository, including after symlink resolution. Missing, binary and oversized
content have distinct results. The per-object ceiling is 16 MiB and the native
batch budget is 32 MiB. File bytes retain their original line endings.
