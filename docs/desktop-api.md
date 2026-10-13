# Native Hermes Desktop HTTP bindings

`AsyncHermesDesktop` connects directly to `hermes serve`. It is separate from
`AsyncEdithHermes.remote`, which connects to the EDITH control plane. The native
Desktop application also uses HTTP routes outside the gateway RPC contract.

```python
from edith_hermes import AsyncHermesDesktop

async with AsyncHermesDesktop.remote(
    base_url="http://127.0.0.1:9119",
    profile="family-edith",
    token=local_token,
) as desktop:
    operations = await desktop.capabilities()
    jobs = await desktop.cron.list()
    runs = await desktop.cron.runs(jobs[0]["id"])
    door = desktop.for_profile("door-edith")
    door_jobs = await door.cron.list()
```

Available typed groups are `cron`, `files`, `git`, `skills` and `sessions`.
Cron includes atomic paused creation, edit, pause/resume/removal, trigger,
execution history, delivery targets and blueprints. Mutation preflight rejects
native cross-profile fallback; returned owner metadata is also checked. This
preflight is not a server-side compare-and-swap transaction.
Files expose native tree/text/data-URL operations. Git exposes review, mutation,
branch and worktree operations. Skills expose installed inventory, content
reading/writing, creation and enablement, plus Hub official catalog, sources,
search, preview, safety scanning, install, uninstall and batch update bindings.
Hub installer methods return a process receipt, not installation success. Check
the native action result and saved inventory before confirming completion. SDK
timeouts never replay the installer. Scan policy and user consent belong to the
application's native flow; a scan result is not implicit consent to install.
Sessions expose bounded, owner-checked message pages. This release does not claim
complete coverage of every Desktop REST route or Electron host service.

`AsyncHermesExtensions.prepare_blueprint(key, values)` uses the explicit
`edith.desktop.v1.cron.prepare` operation. It reuses Hermes's native blueprint
validation and returns a profile-owned draft without creating or running a job.
Discover that operation before offering an editable template; the native REST
`instantiate` operation creates a job immediately and must not be used for preview.

Every request carries a concrete profile. `all` is deliberately unavailable in
this bound client: aggregate different profiles explicitly and retain their
ownership metadata. Native job IDs and session IDs are opaque; display names
must not become routing keys. A borrowed HTTP client remains caller-owned.

Mutations are sent once, with redirects disabled by default. A timeout does not
prove failure. Keep an application-owned operation receipt and reconcile saved
state/history before issuing another mutation. `cron.trigger` can wait for the
entire run; its timeout override does not weaken unrelated operations.

Use `capabilities()` to check the running deployment's OpenAPI route inventory.
A documented binding does not mean an older or differently configured deployment
provides it. Authentication failures, absent contracts and malformed discovery
responses are errors, never an empty successful capability list.

These bindings were checked against native Hermes checkout
`04dc7f846cfa921f77c95d42703afdbd9495ca72`, particularly
`hermes_cli/web_routers/{cron,files,git,skills,sessions}.py` and the Desktop API
facades. Source provenance and native API ownership remain with Hermes.

EDITH's optional versioned extension client is separate from native REST/RPC.
`skill_inventory()` returns canonical file identities, revision tokens and optional
legacy invocation aliases, including disabled skills. `toggle_skill(id, revision=...,
enabled=...)` performs a per-skill compare-and-swap under Hermes's configuration
lock. It never writes an inventory snapshot back into configuration. Discover
`skills.inventory` and `skills.toggle` before using these product-owned methods.
`git_diff` preserves patch line endings, `git_apply` checks and atomically applies
selected review patches with fixed Git arguments, and `cron_trigger` / `cron_operation`
wrap the native scheduler claim in a durable request receipt. They require
matching operations in `AsyncHermesExtensions.capabilities()` on the running host.
An app restart can recover a completed receipt without executing again. A native
server crash during execution remains uncertain and blocks another dispatch;
neither missing history nor a timeout establishes failure.
