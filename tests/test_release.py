import re
from pathlib import Path

from edith_hermes import __version__


def test_public_version_matches_the_wheel_build_metadata():
    source=(Path(__file__).parents[1]/'pyproject.toml').read_text()
    assert re.search(r'^version = "([^"]+)"',source,re.MULTILINE).group(1)==__version__
