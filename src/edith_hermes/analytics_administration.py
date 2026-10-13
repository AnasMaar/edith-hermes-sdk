"""Native usage categories with explicit measured/estimated availability metadata."""
from __future__ import annotations

from typing import Any, TypedDict, cast

from .extensions import ExtensionTransport


class UsageAnalytics(TypedDict):
    totals: dict[str, Any]
    daily: list[dict[str, Any]]
    by_model: list[dict[str, Any]]
    by_task: list[dict[str, Any]]
    tools: list[dict[str, Any]]
    skills: dict[str, Any]
    period_days: int
    measuredCostSamples: int
    cacheWriteTokens: int | None
    throughputTokensPerSecond: float | None


class AsyncUsageAdministration:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose one concrete analytics profile')
        self.transport, self.profile = transport, profile

    async def usage(self, days: int = 30) -> UsageAnalytics:
        if not 1 <= days <= 365:
            raise ValueError('Use a period between 1 and 365 days')
        return cast(UsageAnalytics, await self.transport.call('edith.desktop.v1.analytics.usage', profile=self.profile, days=days))
