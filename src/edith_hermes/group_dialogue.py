"""Typed native clarification lifecycle for fenced local hosted-room tasks."""
from __future__ import annotations

from typing import Any, TypedDict, cast

from .extensions import ExtensionTransport


class GroupQuestion(TypedDict):
    sessionId: str
    roomId: str
    memberId: str
    taskId: str
    generation: int
    request: dict[str, Any]


class AsyncGroupDialogue:
    def __init__(self, connection: ExtensionTransport):
        self.connection = connection

    async def pending(self, room_id: str) -> list[GroupQuestion]:
        result = await self.connection.call('edith.desktop.v1.groups.questions', room_id=room_id)
        return cast(list[GroupQuestion], result['questions'])

    async def answer(self, room_id: str, *, task_id: str, execution_generation: int,
                     request_id: str, answers: dict[str, str | list[str] | None] | None) -> dict[str, Any]:
        return cast(dict[str, Any], await self.connection.call('edith.desktop.v1.groups.answer-question',
            room_id=room_id, task_id=task_id, execution_generation=execution_generation,
            request_id=request_id, answers=answers))
