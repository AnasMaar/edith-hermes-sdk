# Release readiness

The SDK version is 0.35.0. The owner authorized GitHub and PyPI publication. A tag `v0.35.0` triggers `.github/workflows/release.yml`: it verifies the source, builds the wheel and source distribution once, and transfers those files through an immutable Actions artifact. A separate release job checks their hashes, signs them with Sigstore and uploads them to the GitHub release. Only that job has release-write and signing permissions.

Container publication is separate: all three GHCR image jobs remain disabled unless the repository variable `PUBLISH_GHCR_IMAGES` is explicitly set to `true`.

## Decisions before distribution

- The owner selected MIT for the SDK; `LICENSE` and `project.license` record this choice. The release preflight checks the full standard text and retains the separate upstream notice, but does not establish ownership or legal authority. The upstream notice bundled in `src/edith_hermes/licenses/` covers upstream material.
- Review source ownership and redistribution rights, including `contracts/vendor/nous/inference.openapi.json`, whose snapshot has no identified license. The source distribution contains this verbatim snapshot; the wheel contains generated clients derived from contracts. Assess those separately.
- The source repository and documentation are public. GitHub release and PyPI publication are authorized. The PyPI account owner must register the pending Trusted Publisher described below; GitHub configuration alone cannot establish package ownership on PyPI. No registry token is stored in the repository.
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

## Publish the verified GitHub release to PyPI

In the PyPI account's [pending publisher settings](https://pypi.org/manage/account/publishing/), register:

| Field | Value |
| --- | --- |
| PyPI project name | `edith-hermes-sdk` |
| GitHub owner | `AnasMaar` |
| GitHub repository | `edith-hermes-sdk` |
| Workflow filename | `publish-pypi.yml` |
| Environment | `pypi` |

The repository contains the matching `pypi` environment. PyPI may require a verified email and two-factor authentication. Registering a pending publisher does not reserve a project name; the first successful upload creates the project. See [PyPI's instructions](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).

After the GitHub release finishes and the publisher is registered, run:

~~~sh
gh workflow run publish-pypi.yml --repo AnasMaar/edith-hermes-sdk --ref main -f tag=v0.35.0
~~~

The workflow also accepts a published-release event, but releases created by the release workflow's `GITHUB_TOKEN` do not trigger another workflow. Dispatch PyPI publication explicitly for those releases.

The publisher downloads the existing wheel, source archive, checksum manifest and Sigstore bundles. It verifies the release workflow's tag identity, SHA-256 digests, project name and version before obtaining a short-lived PyPI credential through GitHub OIDC. It never rebuilds the distributions.

Retries first compare the version's existing PyPI files with the GitHub release. Matching files are left in place; only missing files are uploaded. A different hash, unexpected filename or registry error stops publication. When both files already match, the run succeeds without uploading. An immutable published version must never be retagged or replaced.

After publication, compare the public PyPI file digests with `SHA256SUMS` and install `edith-hermes-sdk==0.35.0` in an empty environment outside this checkout. Run the offline tool example there. Record live publication evidence separately from fixture tests.

## Upstream attribution

`contracts/vendor/hermes/gateway-contract.openrpc.json` is pinned to Hermes Agent commit `5470f260cac7bafc7b98676dfba1c12fcddc3234` in `contracts/sources.yaml`; the upstream [MIT license at that commit](https://github.com/NousResearch/hermes-agent/blob/5470f260cac7bafc7b98676dfba1c12fcddc3234/LICENSE) names Nous Research. Its copyright and permission notice is bundled in the wheel and source distribution at `src/edith_hermes/licenses/LICENSE.hermes-agent.txt` (in the installed wheel: `edith_hermes/licenses/`). The pinned snapshot and checksums are documented in `contracts/vendor/README.md`. The Nous inference snapshot was retrieved from its API endpoint; its terms remain to be verified.
