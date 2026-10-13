"""Checked EDITH bindings around the existing Hermes Kanban administration API.

These operations require the explicit native management extension; deployments
without it must report unsupported instead of falling back to an unsafe retry.
"""
from __future__ import annotations

from typing import Any, Literal, Protocol, TypedDict, cast


class ManagementRPC(Protocol):
    async def call(self, method: str, **params: Any) -> Any: ...


TaskAction = Literal['link', 'unlink', 'upload', 'remove-attachment', 'reclaim', 'specify', 'reassign', 'terminate']
BoardAction = Literal['create', 'edit', 'archive', 'remove', 'export', 'import']


class KanbanManagementCapabilities(TypedDict, total=False):
    version: int
    task_actions: list[TaskAction]
    board_actions: list[BoardAction]
    orchestration: bool
    download: bool


class KanbanManagementReceipt(TypedDict, total=False):
    requestId: str
    action: str
    board: str
    profile: str
    status: Literal['pending', 'applied', 'uncertain', 'rejected']
    input: str
    result: dict[str, Any]


class KanbanOrchestration(TypedDict, total=False):
    orchestrator_profile: str
    default_assignee: str
    auto_decompose: bool
    auto_promote_children: bool
    resolved_orchestrator_profile: str
    resolved_default_assignee: str
    active_profile: str


class AsyncKanbanManagement:
    def __init__(self, rpc: ManagementRPC, *, profile: str):
        if not profile or profile.lower() == 'all':
            raise ValueError('Choose a concrete Kanban administration profile')
        self.rpc, self.profile = rpc, profile

    async def _call(self, method: str, **params: Any) -> Any:
        return await self.rpc.call('edith.desktop.v1.kanban.management.' + method, profile=self.profile, **params)

    async def capabilities(self) -> KanbanManagementCapabilities:
        return cast(KanbanManagementCapabilities, await self._call('capabilities'))

    async def board(self, board: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self._call('board', board=board))

    async def task_action(self, board: str, task_id: str, revision: str, *, action: TaskAction, request_id: str, payload: dict[str, Any]) -> KanbanManagementReceipt:
        return cast(KanbanManagementReceipt, await self._call('task-action', board=board, task_id=task_id, revision=revision, action=action, request_id=request_id, payload=payload))

    async def board_action(self, board: str, *, action: BoardAction, request_id: str, revision: str | None, payload: dict[str, Any]) -> KanbanManagementReceipt:
        return cast(KanbanManagementReceipt, await self._call('board-action', board=board, action=action, request_id=request_id, revision=revision, payload=payload))

    async def operation(self, request_id: str) -> KanbanManagementReceipt:
        return cast(KanbanManagementReceipt, await self._call('operation', request_id=request_id))

    async def orchestration(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self._call('orchestration-read'))

    async def change_orchestration(self, revision: str, *, request_id: str, changes: KanbanOrchestration) -> KanbanManagementReceipt:
        return cast(KanbanManagementReceipt, await self._call('orchestration-change', revision=revision, request_id=request_id, changes=changes))

    async def attachment(self, board: str, attachment_id: int) -> dict[str, Any]:
        return cast(dict[str, Any], await self._call('attachment', board=board, attachment_id=attachment_id))
