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
