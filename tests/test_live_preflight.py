from collections import namedtuple
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

spec = spec_from_file_location(
    "edith_verify_live", Path(__file__).resolve().parents[1] / "scripts" / "verify_live.py"
)
verification = module_from_spec(spec)
spec.loader.exec_module(verification)
verify_model_disk_space = verification.verify_model_disk_space


def test_low_disk_preflight_fails_before_model_or_instance_start(monkeypatch):
    usage = namedtuple("Usage", "total used free")
    monkeypatch.setattr(verification.shutil, "disk_usage", lambda path: usage(0, 0, 10 * 1024**3))
    with pytest.raises(RuntimeError, match="only 10.0 GiB available"):
        verify_model_disk_space(16)


def test_preflight_can_be_explicitly_adjusted_for_a_smaller_model(monkeypatch):
    usage = namedtuple("Usage", "total used free")
    monkeypatch.setattr(verification.shutil, "disk_usage", lambda path: usage(0, 0, 10 * 1024**3))
    verify_model_disk_space(8)


@pytest.mark.parametrize("reserve", [-1, float("nan"), float("inf")])
def test_preflight_rejects_invalid_reserve(reserve):
    with pytest.raises(ValueError, match="finite and nonnegative"):
        verify_model_disk_space(reserve)
