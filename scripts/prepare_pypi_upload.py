"""Prepare only missing, hash-matched GitHub release files for PyPI."""

import hashlib
import json
import shutil
import sys
import tarfile
import urllib.error
import urllib.request
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile

tag, source, output = sys.argv[1:]
version = tag.removeprefix("v")
expected = [f"edith_hermes_sdk-{version}-py3-none-any.whl", f"edith_hermes_sdk-{version}.tar.gz"]
source_dir = Path(source)
with ZipFile(source_dir / expected[0]) as wheel:
    meta_path = next(name for name in wheel.namelist() if name.endswith(".dist-info/METADATA"))
    metadata = BytesParser().parsebytes(wheel.read(meta_path))
    if metadata["Name"] != "edith-hermes-sdk" or metadata["Version"] != version:
        raise SystemExit("Wheel metadata does not match the release tag.")
with tarfile.open(source_dir / expected[1], "r:gz") as sdist:
    member = next(item for item in sdist.getmembers() if item.name.count("/") == 1 and item.name.endswith("/PKG-INFO"))
    metadata = BytesParser().parsebytes(sdist.extractfile(member).read())
    if metadata["Name"] != "edith-hermes-sdk" or metadata["Version"] != version:
        raise SystemExit("Source metadata does not match the release tag.")

url = f"https://pypi.org/pypi/edith-hermes-sdk/{version}/json"
try:
    with urllib.request.urlopen(url, timeout=30) as response:
        remote_files = json.load(response)["urls"]
except urllib.error.HTTPError as error:
    if error.code != 404:
        raise
    remote_files = []

remote = {item["filename"]: item["digests"]["sha256"] for item in remote_files}
if set(remote) - set(expected):
    raise SystemExit("PyPI contains unexpected files for this version; refusing to publish.")
output_dir = Path(output)
output_dir.mkdir(parents=True, exist_ok=False)
for filename in expected:
    local = source_dir / filename
    digest = hashlib.sha256(local.read_bytes()).hexdigest()
    if filename in remote:
        if remote[filename] != digest:
            raise SystemExit(f"PyPI has a different hash for {filename}; refusing to publish.")
    else:
        shutil.copyfile(local, output_dir / filename)

if not list(output_dir.iterdir()):
    print("Both PyPI files already match the verified GitHub release.")
else:
    print("Prepared only the files missing from PyPI.")
