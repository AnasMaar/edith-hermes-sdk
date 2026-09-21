"""Local secret resolution for process and container providers."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from .config import Settings


class SecretResolver:
    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def _safe(value: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
            raise RuntimeError(f"Unsafe secret reference component: {value!r}")
        return value

    def resolve(self, reference: dict[str, Any]) -> str:
        name = self._safe(str(reference["name"]))
        key = self._safe(str(reference.get("key") or "value"))
        if self.settings.secret_provider == "environment":
            candidates = [
                "EDITH_SECRET_" + re.sub(r"[^A-Za-z0-9]", "_", f"{name}_{key}").upper(),
                "EDITH_SECRET_" + re.sub(r"[^A-Za-z0-9]", "_", name).upper(),
            ]
            for candidate in candidates:
                value = os.getenv(candidate)
                if value is not None:
                    return value
            raise RuntimeError(f"Secret {name}/{key} is not present in the environment")
        if self.settings.secret_provider == "files":
            root = Path(self.settings.secret_directory).resolve()
            path = (root / name / key).resolve()
            if root not in path.parents:
                raise RuntimeError("Secret reference escapes the configured secret directory")
            try:
                return path.read_text(encoding="utf-8").rstrip("\r\n")
            except FileNotFoundError as exc:
                raise RuntimeError(f"Secret {name}/{key} does not exist") from exc
        raise RuntimeError(f"Unsupported local secret provider: {self.settings.secret_provider}")

    def environment(self, runtime: dict[str, Any]) -> dict[str, str]:
        values: dict[str, str] = {}
        for key, item in (runtime.get("environment") or {}).items():
            if "value" in item:
                values[key] = str(item["value"])
            elif "secretRef" in item:
                values[key] = self.resolve(item["secretRef"])
        return values
