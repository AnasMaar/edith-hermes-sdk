"""Existing native Command Center data; no orchestration backend is recreated."""
from __future__ import annotations

from typing import Any, TypedDict, cast

from .desktop import AsyncHermesDesktop


class NativeSystemStatus(TypedDict, total=False):
    version: str
    model: Any
    gateway: Any
    uptime: float


class NativeUsageAnalytics(TypedDict, total=False):
    totals: dict[str, Any]
    daily: list[dict[str, Any]]
    models: list[dict[str, Any]]


class AsyncCommandCenter:
    def __init__(self, desktop: AsyncHermesDesktop):
        self.desktop = desktop

    async def status(self) -> NativeSystemStatus:
        return cast(NativeSystemStatus, await self.desktop._request('GET', '/api/status'))

    async def usage(self, *, days: int = 30) -> NativeUsageAnalytics:
        if not 1 <= days <= 365:
            raise ValueError('Choose a bounded usage window')
        return cast(NativeUsageAnalytics, await self.desktop._request('GET', '/api/analytics/usage', query={'days': days}))

    async def logs(self, *, lines: int = 200, file: str | None = None, level: str | None = None,
                   component: str | None = None, search: str | None = None) -> dict[str, Any]:
        if not 1 <= lines <= 2000:
            raise ValueError('Choose a bounded log page')
        query: dict[str, Any] = {'lines': lines}
        for key, value in {'file': file, 'level': level, 'component': component, 'search': search}.items():
            if value is not None:
                query[key] = value
        return cast(dict[str, Any], await self.desktop._request('GET', '/api/logs', query=query))
