import re
import subprocess
import sys
from pathlib import Path

import pytest

from edith_hermes import __version__

ROOT = Path(__file__).parents[1]


def test_public_version_matches_the_wheel_build_metadata():
    source = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r'^version = "([^"]+)"', source, re.MULTILINE).group(1) == __version__


def test_release_tag_must_match_version():
    script = ROOT / "scripts" / "check_release_tag.py"
    assert subprocess.run([sys.executable, str(script), f"v{__version__}"], check=False).returncode == 0
    assert subprocess.run([sys.executable, str(script), "v0.0.0"], check=False).returncode != 0


async def test_control_plane_reports_the_installed_sdk_build_version():
    import httpx
    from edith_hermes_control_plane.app import create_app
    from edith_hermes_control_plane.config import Settings

    app = create_app(
        Settings(database_url="sqlite+aiosqlite:///:memory:", enabled_runtime_providers=["external"]),
        start_worker=False,
    )
    async with app.router.lifespan_context(app), httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://release-test"
    ) as client:
        response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["version"] == __version__
    assert app.version == __version__

@pytest.mark.skipif(sys.version_info < (3, 11), reason="release preflight runs on Python 3.13")
def test_release_license_preflight(tmp_path):
    script = ROOT / "scripts" / "check_release_license.py"
    notice = tmp_path / "src/edith_hermes/licenses/LICENSE.hermes-agent.txt"
    notice.parent.mkdir(parents=True)
    notice.write_bytes((ROOT / "src/edith_hermes/licenses/LICENSE.hermes-agent.txt").read_bytes())
    project = tmp_path / "pyproject.toml"
    license_file = tmp_path / "LICENSE"

    def run():
        return subprocess.run([sys.executable, str(script), str(tmp_path)], capture_output=True, text=True, check=False)

    project.write_text('[project]\nname = "test"\n', encoding="utf-8")
    assert run().returncode != 0  # No LICENSE.
    license_file.write_bytes(notice.read_bytes())
    assert run().returncode != 0  # No license metadata.
    project.write_text('[project]\nlicense = "Apache-2.0"\n', encoding="utf-8")
    assert run().returncode != 0  # Metadata disagrees with LICENSE.
    project.write_text('[project]\nlicense = "MIT"\n', encoding="utf-8")
    assert run().returncode == 0
    notice.unlink()
    failure = run()
    assert failure.returncode != 0
    assert str(tmp_path) not in failure.stdout + failure.stderr
