"""Gate external publication on an explicit SDK license and upstream notice.

This check runs under Python 3.13 in the release workflow, not on local builds.
"""

import hashlib
import sys
from pathlib import Path

import tomllib

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
license_id = metadata["project"].get("license")
license_file = root / "LICENSE"
if not license_file.is_file():
    raise SystemExit("Release preflight: add the owner's SDK LICENSE before publication.")
if license_id not in ("MIT", "Apache-2.0"):
    raise SystemExit("Release preflight: set project.license to the chosen SPDX identifier (MIT or Apache-2.0).")

license_text = license_file.read_text(encoding="utf-8")
if license_id == "MIT":
    lines = license_text.splitlines()
    has_copyright = any(line.strip().startswith("Copyright") for line in lines)
    text = " ".join(line for line in lines if not line.strip().startswith("Copyright"))
    digest = hashlib.sha256(" ".join(text.split()).encode()).hexdigest()
    matches = has_copyright and digest == "7c9b48b52decb9837c70f608678129e1ac79e056829c8d1e82e8cdd8aed562f8"
else:
    start = license_text.find("Apache License")
    end = license_text.find("END OF TERMS AND CONDITIONS")
    text = license_text[start:end + len("END OF TERMS AND CONDITIONS")]
    digest = hashlib.sha256(" ".join(text.split()).encode()).hexdigest()
    matches = start >= 0 and end > start and digest == "59d8f0ba87ad9a2f1a431123c8d16646e5b89ba53653e818f16d136d77263c99"
if not matches:
    raise SystemExit("Release preflight: LICENSE does not match project.license or is incomplete.")

notice = root / "src/edith_hermes/licenses/LICENSE.hermes-agent.txt"
if not notice.is_file() or hashlib.sha256(notice.read_text(encoding="utf-8").encode()).hexdigest() != "821556e6336796450ab852d375117b48a4887e71d255794fd6318d99982a5ab6":
    raise SystemExit("Release preflight: restore the pinned upstream Hermes MIT notice.")
print("Release license preflight passed.")
