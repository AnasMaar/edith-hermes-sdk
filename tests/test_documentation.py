"""Checks for executable documentation and a complete, current public reference."""

import ast
import asyncio
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

from edith_hermes import __all__ as exports
from edith_hermes import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_api_reference_covers_every_public_export_without_drift():
    subprocess.run(
        [sys.executable, "scripts/generate_api_reference.py", "--check"],
        cwd=ROOT,
        check=True,
    )
    reference = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "docs/reference").glob("*.md")
    )
    documented = set(re.findall(r"^::: edith_hermes\.(\w+)$", reference, re.MULTILINE))
    assert documented == set(exports)
    assert f"**{__version__}**" in reference


def test_public_documentation_and_examples_are_utf8_and_python_blocks_parse():
    paths = [
        ROOT / "README.md",
        *(ROOT / "docs").rglob("*.md"),
        *(ROOT / "examples").glob("*.py"),
    ]
    fence = chr(96) * 3
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert not text.startswith("\ufeff"), path
        if path.suffix == ".py":
            ast.parse(text, filename=str(path))
        else:
            for block in re.findall(
                rf"^(?:{fence}|~~~)python[^\n]*\n(.*?)^(?:{fence}|~~~)\s*$",
                text,
                re.MULTILINE | re.DOTALL,
            ):
                if '--8<-- "' not in block:
                    ast.parse(block, filename=str(path))


def test_homepage_tool_example_runs_without_network_or_runtime(capsys):
    source = (ROOT / "docs/index.md").read_text(encoding="utf-8")
    block = re.search(r"~~~python\n(.*?)\n~~~", source, re.DOTALL).group(1)
    namespace = {"__name__": "documentation_example"}
    exec(compile(block, "docs/index.md", "exec"), namespace)
    assert capsys.readouterr().out == "shipping_cost\n{'cost': 9.0}\n"
    assert asyncio.run(namespace["shipping_cost"].invoke({"weight_kg": 4})) == {"cost": 18.0}


def test_cookbook_embeds_real_examples_with_no_source_copies():
    cookbook = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "docs/cookbook").glob("*.md")
    )
    snippets = re.findall(r'--8<-- "(examples/[^"]+)"', cookbook)
    assert len(snippets) >= 9
    for snippet in snippets:
        assert (ROOT / snippet).is_file(), snippet
        ast.parse((ROOT / snippet).read_text(encoding="utf-8"), filename=snippet)


def test_documentation_workflow_builds_before_opt_in_pages_deployment():
    workflow = (ROOT / ".github/workflows/docs.yml").read_text(encoding="utf-8")
    assert "mkdocs build --strict" in workflow
    assert "generate_api_reference.py --check" in workflow
    assert "tests/test_documented_examples.py" in workflow
    assert "needs: build" in workflow
    assert "vars.DOCS_PAGES_ENABLED == 'true'" in workflow
    assert "github.event_name != 'pull_request'" in workflow
    assert "pages: write" in workflow
    assert "id-token: write" in workflow
    assert "pull_request_target" not in workflow
    assert "contents: write" not in workflow


def test_docs_api_generator_does_not_import_or_start_optional_runtime():
    spec = importlib.util.spec_from_file_location(
        "documented_api_generator", ROOT / "scripts/generate_api_reference.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    generated = module.pages()
    assert len(generated) == 9
    assert all(path.is_relative_to(ROOT / "docs/reference") for path in generated)
