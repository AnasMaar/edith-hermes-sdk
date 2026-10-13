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

`skill_action(kind, resource, request_id=...)` and `skill_operation(request_id)`
wrap native Hermes skill installation/update/removal with a durable, profile-owned
receipt. A pending/running or uncertain receipt is not completion. Reuse its ID
to reconcile after a lost reply; do not automatically dispatch another action.
The installed extension uses Hermes's bound `skills.manage` installation handler
and its existing Skills Hub update/uninstall functions. It never forces updates
over locally modified skills. A backend restart during an unconfirmed action
can leave an uncertain receipt that requires investigation rather than replay.

`skill_content(identity)` reads a stable canonical skill and its content revision.
`save_skill(identity, revision=..., content=...)` wraps the native foreground
editor under native profile/configuration locks. External changes detected before
a save reject it. It is not a cross-process filesystem transaction; keep the
draft and reload after a conflict. These calls require `skills.content` and
`skills.save` in the running extension's capability inventory. The adapter
should reconcile the actual content after a lost save reply, without writing twice.
