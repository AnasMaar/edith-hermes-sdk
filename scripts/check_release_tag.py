"""Reject a release tag that does not match the installed project metadata."""

import sys
from importlib.metadata import version

if __name__ == "__main__":
    expected = f"v{version('edith-hermes-sdk')}"
    if sys.argv[1:] != [expected]:
        raise SystemExit(f"Release tag must be {expected}")
