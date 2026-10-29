# Release readiness

The SDK version is 0.35.0. A tag `v0.35.0` triggers `.github/workflows/release.yml`, which creates a GitHub release and pushes three container images to GHCR. The workflow does not publish to PyPI. Do not push a release tag until the owner authorizes those external writes and the checks below are complete.

## Decisions before distribution

- The owner selected MIT for the SDK; `LICENSE` and `project.license` record this choice. The release preflight checks the full standard text and retains the separate upstream notice, but does not establish ownership or legal authority. The upstream notice bundled in `src/edith_hermes/licenses/` covers upstream material.
- Review source ownership and redistribution rights, including `contracts/vendor/nous/inference.openapi.json`, whose snapshot has no identified license. The source distribution contains this verbatim snapshot; the wheel contains generated clients derived from contracts. Assess those separately.
- The owner authorized making the source repository public. Confirm the intended registry, package ownership, authentication, and whether the GitHub release and GHCR images should be published before those separate actions. Configure any registry publishing only after approval. The current workflow uses the GitHub token for GHCR and Sigstore's OIDC identity for signing; it has no PyPI publisher configured.
- Ensure CI and Actions billing are available. Do not bypass spending restrictions.
- Confirm whether 0.35.0 can be released unchanged or a new version is needed, including compatibility with existing EDITH installations pinned to 0.35.0. Release versions must match `edith_hermes.__version__`, project metadata, and tag `v<version>`.

## Local verification

From a clean checkout with Python 3.13 and uv installed:

```sh
uv sync --frozen --group dev --group docs
uv run python scripts/check_release_tag.py v0.35.0
uv run python scripts/check_release_license.py
uv run pytest
uv run ruff check .
uv run mypy src/edith_hermes src/edith_hermes_rpc
uv run mypy --ignore-missing-imports services/control_plane/edith_hermes_control_plane services/runtime_bridge/edith_hermes_runtime_bridge
uv run python scripts/validate_contracts.py
uv run python scripts/generate_sdk.py
git diff --exit-code -- src/edith_hermes/generated
uv run --frozen --group docs python scripts/generate_api_reference.py --check
uv run --frozen --group docs mkdocs build --strict
uv build --out-dir build/release-check
uv run python scripts/verify_release_artifacts.py build/release-check v0.35.0 --require-license
uv run twine check --strict build/release-check/*.whl build/release-check/*.tar.gz
```

Use an empty output directory for the build. CI additionally checks a clean wheel installation, Redocly lint, containers, and PostgreSQL integration. Inspect both distributions before release; the wheel contains SDK, RPC, and control-plane Python packages, and the source archive includes contracts, scripts, examples, services, and project branding. Neither is intended to include a recovered Codex renderer. Signing and checksums attest the artifacts the workflow builds; they do not independently establish ownership or licensing.

## Upstream attribution

`contracts/vendor/hermes/gateway-contract.openrpc.json` is pinned to Hermes Agent commit `5470f260cac7bafc7b98676dfba1c12fcddc3234` in `contracts/sources.yaml`; the upstream [MIT license at that commit](https://github.com/NousResearch/hermes-agent/blob/5470f260cac7bafc7b98676dfba1c12fcddc3234/LICENSE) names Nous Research. Its copyright and permission notice is bundled in the wheel and source distribution at `src/edith_hermes/licenses/LICENSE.hermes-agent.txt` (in the installed wheel: `edith_hermes/licenses/`). The pinned snapshot and checksums are documented in `contracts/vendor/README.md`. The Nous inference snapshot was retrieved from its API endpoint; its terms remain to be verified.
