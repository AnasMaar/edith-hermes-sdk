"""Inspect the exact distributions produced by ``uv build``."""

import sys
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

import tomllib

directory = Path(sys.argv[1])
wheels = list(directory.glob("*.whl"))
sdists = list(directory.glob("*.tar.gz"))
if len(wheels) != 1 or len(sdists) != 1:
    raise SystemExit("Expected exactly one wheel and one source distribution")

with zipfile.ZipFile(wheels[0]) as wheel:
    names = wheel.namelist()
    metadata = BytesParser().parsebytes(wheel.read(next(n for n in names if n.endswith(".dist-info/METADATA"))))
    assert metadata["Name"] == "edith-hermes-sdk"
    assert metadata["Version"] == sys.argv[2].removeprefix("v")
    assert "edith_hermes/licenses/LICENSE.hermes-agent.txt" in names
    assert all(not n.lower().startswith(("assets/", "renderer/")) for n in names)
    if "--require-license" in sys.argv[3:]:
        project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
        assert metadata["License-Expression"] == project["license"]
        license_name = next(n for n in names if n.endswith(".dist-info/licenses/LICENSE"))
        assert wheel.read(license_name).decode().splitlines() == Path("LICENSE").read_text(encoding="utf-8").splitlines()

with tarfile.open(sdists[0]) as sdist:
    names = sdist.getnames()
    assert any(n.endswith("/src/edith_hermes/licenses/LICENSE.hermes-agent.txt") for n in names)
    assert any(n.endswith("/contracts/vendor/hermes/gateway-contract.openrpc.json") for n in names)
    if "--require-license" in sys.argv[3:]:
        assert any(n.count("/") == 1 and n.endswith("/LICENSE") for n in names)

print(f"Verified {wheels[0].name} and {sdists[0].name}")
