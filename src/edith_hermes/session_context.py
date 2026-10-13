"""Read-only context discovery over the existing profile-scoped Desktop API."""
from __future__ import annotations

from typing import TypedDict, cast

from .desktop import AsyncHermesDesktop


class ContextSession(TypedDict, total=False):
    id: str
    profile: str
    title: str | None
    preview: str | None
    _lineage_root_id: str


class AsyncSessionContexts:
    def __init__(self, desktop: AsyncHermesDesktop):
        self.desktop = desktop

    async def list(self, *, limit: int = 30) -> list[ContextSession]:
        if not 1 <= limit <= 100:
            raise ValueError("Session context limit must be between 1 and 100")
        result = await self.desktop._request("GET", "/api/sessions", query={
            "limit": limit, "offset": 0, "min_messages": 1, "archived": "exclude", "order": "recent", "full": "false"})
        if not isinstance(result, dict) or not isinstance(result.get("sessions"), list):
            raise ValueError("Hermes returned an invalid session inventory")
        if result.get("storage", {}).get(self.desktop.profile) == "corrupt":
            raise ValueError("The owning profile's session store is unavailable")
        for row in result["sessions"]:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str) or row.get("profile") != self.desktop.profile:
                raise ValueError("The returned session belongs to another profile")
        return cast(list[ContextSession], result["sessions"])
