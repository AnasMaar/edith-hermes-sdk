# Documentation and SDK verification

This page records the release-preparation checks performed on October 29, 2026.
It describes checked source, publication checks and local fixtures; it does not certify untested services.

## Published v0.35.0 artifacts

[The GitHub release](https://github.com/AnasMaar/edith-hermes-sdk/releases/tag/v0.35.0)
was published from source revision `c203496` by the successful
[release workflow](https://github.com/AnasMaar/edith-hermes-sdk/actions/runs/40952153187).
[CI for that same revision](https://github.com/AnasMaar/edith-hermes-sdk/actions/runs/40952135020)
passed all 12 jobs. The release verification suite passed **606 tests**, including six
new checks for absent, partial, complete, conflicting and unavailable PyPI inventories.

Both published distributions were downloaded again and independently checked against
the release's SHA-256 manifest and Sigstore bundles. Their signing identity matched
`release.yml@refs/tags/v0.35.0`. Strict Twine validation and licence/content inspection
passed on those downloaded files. The published wheel was installed into an empty
Python 3.13 environment outside the checkout; isolated imports reported version 0.35.0
from site-packages, and the offline tool example returned `2`.

[PyPI v0.35.0](https://pypi.org/project/edith-hermes-sdk/0.35.0/) was then published
through GitHub OIDC by [the publishing workflow](https://github.com/AnasMaar/edith-hermes-sdk/actions/runs/40956421392).
The public PyPI inventory reported exactly the wheel and source archive, with hashes
matching the signed GitHub release. PyPI displays provenance for both files.
A clean, cache-disabled installation from `https://pypi.org/simple` into a separate
Python 3.13 environment passed isolated imports and the offline tool example (`2`).

[A second publishing run](https://github.com/AnasMaar/edith-hermes-sdk/actions/runs/40956577853)
verified both existing file hashes and skipped the upload step, confirming the completed
release's retry path against the live registry. The first local JSON lookup briefly
returned 404 after the successful upload; the later lookup returned the complete
inventory. Account for registry propagation when reconciling a just-published release.
The [release guide](readiness.md) describes publisher setup and digest reconciliation.

## GitHub CI and hosted-site acceptance

[CI for source revision 91a5554](https://github.com/AnasMaar/edith-hermes-sdk/actions/runs/40944137768)
passed all 12 jobs: Linux Python 3.10–3.14, Windows Python 3.14, macOS Python 3.13,
type/lint/contract/package checks, PostgreSQL integration and all three container images.
The Linux Python 3.13 run passed **600 tests**. The non-root control-plane image probe
checked its actual SQLite startup and build version; all images retained the SDK licence.

[The documentation workflow](https://github.com/AnasMaar/edith-hermes-sdk/actions/runs/40944137812)
deployed the site. Anonymous requests confirmed both the public MIT repository and the
hosted documentation. The browser checks also passed against the actual GitHub Pages
deployment: light/dark themes, search, source snippets, API signatures, 38 internal links,
and mobile navigation without page-level overflow.

CI exposed and helped fix two issues missed by the first local run: the pytest console
entry point could not import the repository examples, and the built control-plane image
reported an old hardcoded version. The final suite covers that build identity.

Fresh wheel and source archives passed strict Twine **7.0.0** validation and clean wheel
installation on Python 3.10 and 3.13. Their metadata version is 2.5; an older Twine tool
selected by a pre-7 version constraint rejected that valid metadata. CI and release
validation now use a compatible bounded Twine version.

## Verification layers

The local SDK run passed **599 tests**. The documented recipes have **14 protocol/example
tests**, and the site has six additional checks covering export coverage, source drift,
UTF-8, Python snippet syntax, executable onboarding and deployment policy.
Both configured mypy checks, Ruff, contract validation, the MIT/tag preflight, fresh
distribution inspection and clean wheel installation passed.

The browser review checked light/dark pages, keyboard search, paste, result navigation,
embedded source, rendered signatures and a 390-pixel mobile layout. It found and fixed
a search-opening/paste problem and a low-contrast secondary button. The final check
followed 38 local navigation links and measured no page-level horizontal overflow.
The generated reference documents **105 public exports**.

The inspected local homepage was approximately 47 KB of decoded HTML and reached
DOMContentLoaded in about 170–210 ms on this machine. That is a localhost development
measurement, not a claim about internet latency, mobile hardware or live backend speed.

| Layer | What it establishes | What it does not establish |
| --- | --- | --- |
| SDK unit and protocol tests | Serialization, routing, ownership, receipts, errors and event handling | A deployment implements every bound operation |
| Runnable example fixtures | Example logic invokes the public API with expected scoped requests and WebSocket frames | Live model quality, billing, external account access |
| Static type checks | SDK and server packages satisfy their configured type checks | Correct provider configuration |
| Generated-code check | Generated SDK and reference pages match their sources | Compatibility with an uninspected future Hermes version |
| Distribution inspection | Wheel/source contents, version consistency and retained notices | A public licence grant for unrelated material |
| Clean wheel installation | Published-package imports work outside the repository | Complete Docker/Kubernetes deployment certification |
| Strict documentation build | Navigation, source includes and resolvable API objects | Live hosting until Pages deployment succeeds |
| Browser inspection | Rendered layouts, search, themes, navigation and code blocks | Native desktop or physical audio behavior |

## Reproduce the checks

~~~sh
uv sync --frozen --group dev --group docs
uv run pytest
uv run ruff check .
uv run mypy src/edith_hermes src/edith_hermes_rpc
uv run mypy --ignore-missing-imports services/control_plane/edith_hermes_control_plane services/runtime_bridge/edith_hermes_runtime_bridge
uv run python scripts/validate_contracts.py
uv run python scripts/generate_sdk.py
uv run python scripts/generate_api_reference.py --check
uv run mkdocs build --strict
uv build --out-dir build/release-check
uv run python scripts/verify_release_artifacts.py build/release-check v0.35.0
~~~

Use an empty package output directory. The [release guide](readiness.md) describes clean
installation and publication prerequisites. The
[example tests](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/tests/test_documented_examples.py)
exercise HTTP, embedded-driver and local WebSocket fixtures without private credentials.

## Live prerequisites

End-to-end inference requires a reachable model provider and an authorized runtime.
Container orchestration requires Docker or a configured Kubernetes cluster.
Hosted connector sign-in requires supported backend methods and an external account.
Bot/group mutations require disposable profiles and actual owner permissions.

No user Family EDITH or Door EDITH profile was modified to verify these docs.
Fixture test success must not be described as successful live OAuth, cloud provisioning
or physical audio validation.
