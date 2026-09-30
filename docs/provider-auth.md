# Provider authentication

Provider OAuth is separate from control-plane authentication and MCP-tool OAuth.
You can use it through `Hermes.local(...)` or `Hermes.remote(...)`; PostgreSQL,
OIDC and KMS are not required. Install the control-plane extra for local runtimes.

## An existing instance and a specific profile

Runnable consent example: [examples/provider_login.py](../examples/provider_login.py).

```python
from edith_hermes import Hermes, ProviderLoginError

async with Hermes.remote(base_url="http://localhost:8080") as hermes:
    instance = await hermes.open_instance(instance_id)
    adam = instance.agent("Adam")
    codex = adam.providers("openai-codex")

    print(await codex.status())
    login = await codex.login(open_browser=True)  # Browser opening is opt-in.
    print(login.verification_url, login.user_code)
    try:
        result = await login.wait()  # Requires the user to approve at the provider.
    except ProviderLoginError as exc:
        print(exc.login["status"], exc.login["errorCode"])
        raise

    # Login authenticates only; choose the profile's model separately.
    await adam.update(provider="openai-codex", model=chosen_model_id)
```

`instance_id` and `chosen_model_id` are application inputs, not hard-coded example
IDs. Select a model supported by your provider/account, for example from
`adam.native.model.options()`. Pass the control-plane `token` to `Hermes.remote`
only if your deployment requires it. That token is NOT the model-provider token.

For a headless/container environment use `login()` without `open_browser` and
display the URL/code in your frontend. The user can approve on another device.
The SDK does not approve consent, enable device auth in account settings, or
sign into an issuer on the user's behalf.

OpenAI's [Codex authentication documentation](https://learn.chatgpt.com/docs/auth)
distinguishes ChatGPT-plan authentication from API-key billing and describes
device-auth settings/eligibility. This adapter delegates to Hermes' existing
`openai-codex` flow; it is not a generic implementation of the separate Sign in
with ChatGPT token-sharing preview. Hosted/paid products must check the applicable
[OpenAI integration requirements](https://developers.openai.com/siwc/token-sharing-open-source).
Successful login does not guarantee model entitlement or quota.

## Discovery, polling, cancellation and accounts

```python
catalog = await adam.providers.list()  # Dynamic native catalog, including plugins.
for provider in catalog["items"]:
    print(provider["id"], provider["flow"], provider["loginSupported"])

login = await codex.login(idempotency_key="onboarding-request-123")
print(await login.get())
saved_id = login.id

# A new SDK handle/control-plane process can attach to the same pending login.
reattached = codex.logins(saved_id)
await reattached.get()  # Populates its verification_url/user_code/info properties.
await reattached.wait(timeout=900)

# Alternative: explicitly stop a still-pending native login.
# await reattached.cancel()

accounts = await codex.accounts.list()
# Indices are native, one-based positions, NOT stable account IDs.
# Re-list immediately before removal and serialize modifications per profile.
# await codex.accounts(accounts["items"][0]["index"]).remove()

# Clears Hermes-managed auth for this profile, not issuer-side consent.
# await codex.disconnect()
```

`wait()` uses the advertised polling interval (override `poll_interval` if needed).
It returns an approved login or raises `ProviderLoginError` with the safe terminal
record. `raise_on_failure=False` returns denied/expired/cancelled/failed records.
A wait timeout or cancellation of the Python task does NOT cancel the native flow.
Use `cancel()` explicitly. Cancelling an already-approved login returns 409;
disconnect explicitly to clear credentials. Cancellation racing with approval
cannot undo already-granted consent or issuer-side tokens.

`logins.start()` exposes the typed wire response if you prefer to store only the
login ID/instructions. The same eight OpenAPI operations are also available under
`AsyncEdithHermes.providers` and the synchronous `EdithHermes.providers` namespace.
They are the same contract/implementation, not a second feature set.

## Credential custody and status

- Every login is bound to its control-plane owner, instance, profile and provider.
  Moving a login ID to another scope returns 404 before any native request.
- Native profile names are canonicalized (`Adam` → `adam`) at the HTTP boundary;
  your display name and SDK profile ID stay unchanged.
- Hermes performs device polling, token exchange, credential persistence and
  supported-provider refresh. The SDK never receives access/refresh tokens,
  device secrets, token previews or raw native error messages. The registry stores
  only scoped login metadata and the user-facing verification challenge.
- Persist Hermes home/volumes if credentials must survive runtime recreation.
  Pending login sessions are process-local in Hermes; a runtime restart produces
  `expired` / `runtime_session_lost` and requires starting a fresh flow. Restarting
  only the control plane preserves mappings if its registry persists.
- Terminal records are updated atomically so a stale poll cannot resurrect them
  across SQLite/PostgreSQL workers. Instance/profile deletion removes their rows.
- `authenticated` means credentials are present, not that an issuer accepted them.
  Expiry/revocation is reported when the native response establishes it; otherwise
  `validity` is `unknown`. Native Codex cards can omit expiry/refresh metadata.
  An account's `lastStatus=401` alone is NOT proof of revocation. This facade does
  not introduce a speculative manual refresh or issuer-validation endpoint.
- Account listing covers Hermes' credential pool, not every issuer account.
  Singleton credentials may not appear, and repeat login may replace native
  singleton credentials rather than adding a separate pooled account. Native
  account removal lacks compare-and-delete; do not treat indices as durable IDs.
- Profiles isolate configuration, not hostile users. Use separate runtimes for
  untrusted users, protect control-plane access and native credential volumes,
  and ensure a user's device code is shown only to that user.

## Compatibility and extensibility

The contract is [providers.openapi.yaml](../contracts/openapi/providers.openapi.yaml).
Its adapter follows upstream `oauth.py`/`ops.py` at Hermes revision
`16fe260aab45a524df94c8f635352fd9e6e66fe5`; it does not invent native RPC methods.
The existing 219-method pinned OpenRPC contract remains unchanged.

The native catalog determines provider availability. Current dashboard device-code
flows include `openai-codex`, `nous`, `minimax-oauth` and `xai-oauth`. External/CLI-only
providers (including catalog-added plugins without a dashboard flow) are discoverable
with their CLI/docs metadata and explicit `loginSupported=False`. Starting those
returns 501. The native submit-code endpoint currently rejects submissions, so this
SDK does not advertise unsupported callback/PKCE completion methods. Supporting a
new flow requires a real native adapter and tests; OAuth alone does not make any
arbitrary provider interchangeable or waive its terms.

Docker/process/native-WebSocket connections use the dashboard HTTP origin with
the same runtime token or isolated password-cookie jar. Reverse-proxy prefixes
are preserved. Kubernetes uses the runtime bridge's allowlisted provider-auth
proxy: it accepts only the documented routes and a `profile` query, rejects
arbitrary targets/dashboard routes, and withholds native secrets/errors.
Build the bridge from this checkout and select that image explicitly. Previously
published bridges do not contain this proxy; they return unsupported capability
errors until upgraded. This source update does not publish a registry image.

## Verification (2026-09-30)

The complete suite now contains **435 tests** (including 49 dedicated provider-auth/
bridge checks). Ruff, strict SDK/backend mypy, five OpenAPI contracts, Redocly lint,
deterministic generation and source/wheel packaging are checked alongside the tests.

Live discovery passed for both Adam and Anas on the installed official Docker image
(eight native providers), and on kind with a locally rebuilt bridge. PostgreSQL
terminal-state protection passed in a disposable local container. An initial native
HTTP rejection of display-case profile names exposed the canonical-name mismatch;
the adapter now normalizes at the HTTP boundary, and the reruns passed. Test-owned
containers, workloads, services, secrets and PVCs were removed; the existing kind
cluster and original images/models were preserved.

The locally tested bridge is `edith-runtime-bridge:provider-auth-20260930`, image ID
`sha256:0446690bd72a6fa0a9f81e0014f0c4af54120c5bab00864078f31892101d1559`.
It is available in local Docker/kind only, not published to a registry.

Protocol tests use scripted native endpoints—not real OAuth-provider sign-ins—and
cover approval/failure/expiry/cancel, consent timeout, idempotency, reattachment,
scope isolation, redaction, cookie auth/prefixes, the bridge allowlist, and terminal
state concurrency. Run `uv run pytest` for the complete suite.

Read-only live checks (no login, paid model or account credentials) are available:

```sh
uv run python scripts/verify_provider_auth_live.py
uv run python scripts/verify_kubernetes_live.py --bridge-image YOUR_CURRENT_BRIDGE_IMAGE
uv run python scripts/verify_postgres_live.py
```

Docker checks the full typed SDK → local control plane → native dashboard path for
Adam and Anas. Kubernetes checks gateway → rebuilt bridge → native dashboard for
both profiles. PostgreSQL checks stale poll protection alongside existing storage
checks. Actual issuer approval, refresh, revoked-account recovery and paid model
inference require deliberate user sign-in and are not certified by these tests.
