# Contributing

Use Python 3.10–3.14 and uv. Install the development environment with `uv sync --frozen --group dev`, then run `uv run pytest` and `uv run ruff check .`. Changes to contracts require `uv run python scripts/validate_contracts.py` and `uv run python scripts/generate_sdk.py`; review and commit generated changes with the source contract. See [release readiness](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/docs/release/readiness.md) for distribution checks and unresolved licensing decisions.
