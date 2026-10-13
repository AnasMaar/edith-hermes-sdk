"""Profile-bound native histories used by Hermes Desktop's Artifacts index.

Hermes has no artifact REST inventory. Its native page indexes paginated
session messages; these bindings expose those existing routes without adding
an alternative persistence or execution backend.
"""
from __future__ import annotations

from typing import Any, TypedDict, cast
from urllib.parse import quote

from .desktop import AsyncHermesDesktop


class ArtifactSession(TypedDict, total=False):
    id: str
    profile: str
    title: str
    started_at: float
    last_active: float


class ArtifactSessionPage(TypedDict, total=False):
    sessions: list[ArtifactSession]
    total: int
    has_more: bool


class HistoryMessage(TypedDict, total=False):
    id: int | str
    role: str
    content: Any
    timestamp: float
    tool_name: str


class ArtifactMessagePage(TypedDict, total=False):
    session_id: str
    profile: str
    messages: list[HistoryMessage]
    pagination: dict[str, Any]


class AsyncArtifactHistory:
    def __init__(self, desktop: AsyncHermesDesktop):
        self.desktop = desktop

    async def sessions(self, *, limit: int = 50, offset: int = 0) -> ArtifactSessionPage:
        if not 1 <= limit <= 500 or offset < 0:
            raise ValueError('Choose a bounded session page')
        result = await self.desktop._request('GET', '/api/profiles/sessions', query={
            'limit': limit, 'offset': offset, 'min_messages': 1,
            'archived': 'exclude', 'order': 'recent',
        })
        if not isinstance(result, dict) or not isinstance(result.get('sessions'), list):
            raise ValueError('Native session inventory is unavailable')
        if any(row.get('profile') != self.desktop.profile for row in result['sessions']):
            raise ValueError('The artifact inventory belongs to another profile')
        return cast(ArtifactSessionPage, result)

    async def messages(self, session_id: str, *, limit: int = 100, offset: int = 0) -> ArtifactMessagePage:
        if not session_id or not 1 <= limit <= 500 or offset < 0:
            raise ValueError('Choose a bounded canonical session history page')
        result = await self.desktop._request('GET', '/api/sessions/' + quote(session_id, safe='') + '/messages', query={
            'limit': limit, 'offset': offset, 'order': 'oldest',
            'include_compacted': 'true', 'inline_images': 'false',
        })
        if not isinstance(result, dict) or result.get('profile') != self.desktop.profile or not isinstance(result.get('messages'), list):
            raise ValueError('The artifact history belongs to another profile')
        return cast(ArtifactMessagePage, result)

    async def file(self, session_id: str, path: str) -> dict[str, Any]:
        if not session_id or not path:
            raise ValueError('Choose an artifact on its canonical originating session')
        return cast(dict[str, Any], await self.desktop._request('GET', '/api/fs/read-data-url', query={'session_id': session_id, 'path': path}))
