"""Translate the public profile contract into native Hermes parameters."""

from __future__ import annotations

import json
from typing import Any


def create_params(profile: dict[str, Any]) -> dict[str, Any]:
    aliases = {
        "cloneFrom": "clone_from",
        "cloneAll": "clone_all",
        "cloneChannels": "clone_channels",
        "mirrorCredentials": "mirror_credentials",
    }
    result = {
        aliases.get(k, k): v for k, v in profile.items() if k not in {"config", "includeSkills"}
    }
    if "includeSkills" in profile:
        result["no_skills"] = not profile["includeSkills"]
    return result


async def configure(gateway: Any, connection: dict[str, Any], profile: dict[str, Any]) -> None:
    def flatten(data: dict[str, Any], prefix: str = "") -> list[tuple[str, Any]]:
        values = []
        for key, value in data.items():
            dotted = prefix + key
            values.extend(
                flatten(value, dotted + ".") if isinstance(value, dict) else [(dotted, value)]
            )
        return values

    for key, value in flatten(profile.get("config") or {}):
        encoded = value if isinstance(value, str) else json.dumps(value)
        response = await gateway.invoke(
            connection,
            "cli.exec",
            {
                "profile": profile["name"],
                "argv": ["-p", profile["name"], "config", "set", key, encoded],
            },
        )
        result = response.get("result") or {}
        if result.get("blocked") or result.get("code", 0) != 0:
            raise RuntimeError(f"Hermes rejected profile configuration key {key!r}")
    fields = {k: profile[k] for k in ("soul", "description", "model", "provider") if k in profile}
    if fields:
        # A custom endpoint must exist before Hermes can validate/pin its model.
        response = await gateway.invoke(
            connection,
            "profiles.configure",
            {"name": profile["name"], **fields},
        )
        result = response.get("result") or {}
        if any(value is False for value in result.get("applied", {}).values()):
            raise RuntimeError(
                "Hermes could not apply the profile model/provider; check its configuration"
            )
