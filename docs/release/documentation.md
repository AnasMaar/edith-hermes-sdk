# Documentation delivery

## Build locally

Use Python 3.13 and uv. From a checkout of this repository:

~~~sh
uv sync --frozen --group dev --group docs
uv run python scripts/generate_api_reference.py --check
uv run mkdocs build --strict
uv run mkdocs serve
~~~

The static site is written to the ignored site directory. API documentation resolves
Python source without starting a control plane. Cookbook pages embed the example
files directly. The build requires no model token or live runtime.

## GitHub Pages

The public documentation address is
[anasmaar.github.io/edith-hermes-sdk/](https://anasmaar.github.io/edith-hermes-sdk/).
This address is not evidence that deployment has happened.

The owner selected the MIT licence and authorized making the SDK repository public.
The site is built from that repository and deployed using GitHub Pages. The separate
EDITH desktop application repository remains outside this documentation deployment.

The documentation workflow builds and checks the site. Configure GitHub Pages for
GitHub Actions and set the repository variable DOCS_PAGES_ENABLED to true to enable
deployment from main. Pull requests build an artifact without deployment rights.
Never copy development state, tokens,
environment files or private audit logs into the public site.

## What is published

The site includes public-facing guides, Python API signatures, original example source
and project documentation. It does not include recovered renderer assets, an SDK wheel,
live configuration or model credentials.

Before publishing, review the generated site and retained third-party notices.
The source links point to the SDK repository's default branch; new reference pages
and examples become available there when the documentation change is merged.

## Maintaining the documentation

1. Update public Python interfaces and their docstrings.
2. Run the API-reference generator and commit the updated reference pages.
3. Update or add a runnable example and its protocol fixture tests.
4. Build with strict validation and inspect light/dark and narrow layouts.
5. Deploy the checked static build through the selected Pages repository.

The README takes layout cues from the public Python SDKs maintained by
[Anthropic](https://github.com/anthropics/anthropic-sdk-python) and
[OpenAI](https://github.com/openai/openai-python): installation first, short working
examples, explicit errors and practical development commands. The site separates
onboarding, recipes, guides and reference in the manner of
[Pydantic's documentation](https://pydantic.dev/docs/ai/overview/).
Their prose, logos and artwork are not bundled into this project.
