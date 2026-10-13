"""Hermes's existing optional Kanban plugin REST API, with explicit board scope."""
from __future__ import annotations

from typing import Any, TypedDict, cast
from urllib.parse import quote

from .desktop import AsyncHermesDesktop


class KanbanTask(TypedDict, total=False):
    id: str
    title: str
    status: str
    assignee: str
    priority: int
    body: str


class KanbanBoard(TypedDict, total=False):
    tasks: list[KanbanTask]
    settings: dict[str, Any]


class AsyncKanban:
    def __init__(self, desktop: AsyncHermesDesktop, *, board: str):
        if not board or board != board.strip():
            raise ValueError('Choose an explicit owning Kanban board')
        self.desktop, self.board = desktop, board

    async def _request(self, method: str, path: str, body: Any = None) -> Any:
        return await self.desktop._request(method, '/api/plugins/kanban' + path, query={'board': self.board}, body=body)

    async def snapshot(self) -> KanbanBoard:
        return cast(KanbanBoard, await self._request('GET', '/board'))

    async def task(self, task_id: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self._request('GET', '/tasks/' + quote(task_id, safe='')))

    async def orchestration(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self._request('GET', '/orchestration'))
