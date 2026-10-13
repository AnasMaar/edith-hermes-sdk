"""Hermes's existing optional Kanban plugin REST API, with explicit board scope."""

from __future__ import annotations

from typing import Any, Protocol, TypedDict, cast
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
    columns: list[dict[str, Any]]
    tenants: list[str]
    assignees: list[str]
    latest_event_id: int
    now: int


class KanbanRPC(Protocol):
    async def call(self, method: str, **params: Any) -> Any: ...


class AsyncCheckedKanban:
    """Explicit EDITH extension: native rules with CAS and durable receipts."""

    def __init__(self, rpc: KanbanRPC, *, board: str, profile: str):
        if not board or board != board.strip():
            raise ValueError("Choose an explicit owning Kanban board")
        if not profile or profile.lower() == "all":
            raise ValueError("Choose a concrete Kanban administration profile")
        self.rpc, self.board, self.profile = rpc, board, profile

    async def _call(self, method: str, **params: Any) -> Any:
        return await self.rpc.call(
            "edith.desktop.v1.kanban." + method, board=self.board, profile=self.profile, **params
        )

    async def capabilities(self) -> dict[str, bool]:
        return cast(
            dict[str, bool],
            await self._call("capabilities"),
        )

    async def read(self, task_id: str) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._call("read", task_id=task_id),
        )

    async def change(
        self,
        *,
        request_id: str,
        patch: dict[str, Any],
        task_id: str | None = None,
        revision: str | None = None,
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._call(
                "change",
                request_id=request_id,
                task_id=task_id,
                revision=revision,
                patch=patch,
            ),
        )

    async def operation(self, request_id: str) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._call("operation", request_id=request_id),
        )


class AsyncKanban:
    def __init__(self, desktop: AsyncHermesDesktop, *, board: str):
        if not board or board != board.strip():
            raise ValueError("Choose an explicit owning Kanban board")
        self.desktop, self.board = desktop, board

    async def _request(self, method: str, path: str, body: Any = None) -> Any:
        return await self.desktop._request(
            method, "/api/plugins/kanban" + path, query={"board": self.board}, body=body
        )

    async def snapshot(self) -> KanbanBoard:
        return cast(KanbanBoard, await self._request("GET", "/board"))

    async def boards(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self._request("GET", "/boards"))

    async def workflow(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self._request("GET", "/workflow"))

    async def task(self, task_id: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self._request("GET", "/tasks/" + quote(task_id, safe="")))

    async def orchestration(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self._request("GET", "/orchestration"))
