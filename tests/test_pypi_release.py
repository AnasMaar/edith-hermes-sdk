"""Check PyPI reconciliation without contacting a registry."""

import hashlib
import io
import json
import runpy
import sys
import tarfile
import urllib.error
from pathlib import Path
from zipfile import ZipFile

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "prepare_pypi_upload.py"


@pytest.mark.parametrize("state", ["missing", "partial", "complete", "mismatch", "unexpected", "unavailable"])
def test_reconcile_pypi_files(monkeypatch, tmp_path, state, capsys):
    source = tmp_path / "release"
    source.mkdir()
    wheel = source / "edith_hermes_sdk-0.35.0-py3-none-any.whl"
    sdist = source / "edith_hermes_sdk-0.35.0.tar.gz"
    with ZipFile(wheel, "w") as archive:
        archive.writestr("sdk.dist-info/METADATA", "Name: edith-hermes-sdk\nVersion: 0.35.0\n")
    with tarfile.open(sdist, "w:gz") as archive:
        content = b"Name: edith-hermes-sdk\nVersion: 0.35.0\n"
        member = tarfile.TarInfo("edith_hermes_sdk-0.35.0/PKG-INFO")
        member.size = len(content)
        archive.addfile(member, io.BytesIO(content))
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
    wheel_record = {"filename": wheel.name, "digests": {"sha256": digest}}
    sdist_record = {"filename": sdist.name, "digests": {"sha256": hashlib.sha256(sdist.read_bytes()).hexdigest()}}
    records = {"partial": [wheel_record], "complete": [wheel_record, sdist_record], "mismatch": [{"filename": wheel.name, "digests": {"sha256": "0" * 64}}], "unexpected": [{"filename": "unexpected.whl", "digests": {"sha256": "0" * 64}}]}

    def fetch(url, timeout):
        assert url == "https://pypi.org/pypi/edith-hermes-sdk/0.35.0/json"
        if state in {"missing", "unavailable"}:
            code = 404 if state == "missing" else 503
            raise urllib.error.HTTPError(url, code, "error", {}, None)
        return io.BytesIO(json.dumps({"urls": records[state]}).encode())

    monkeypatch.setattr("urllib.request.urlopen", fetch)
    target = tmp_path / "upload"
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "v0.35.0", str(source), str(target)])
    if state == "mismatch":
        with pytest.raises(SystemExit, match="different hash"):
            runpy.run_path(str(SCRIPT), run_name="__main__")
        return
    if state == "unexpected":
        with pytest.raises(SystemExit, match="unexpected files"):
            runpy.run_path(str(SCRIPT), run_name="__main__")
        return
    if state == "unavailable":
        with pytest.raises(urllib.error.HTTPError):
            runpy.run_path(str(SCRIPT), run_name="__main__")
        return
    runpy.run_path(str(SCRIPT), run_name="__main__")
    actual = {p.name for p in target.iterdir()}
    assert actual == {"missing": {wheel.name, sdist.name}, "partial": {sdist.name}, "complete": set()}[state]
    if state == "complete":
        assert "already match" in capsys.readouterr().out
