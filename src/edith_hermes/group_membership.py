"""Native idle fences for presentation lineages over frozen Hermes rooms."""
from __future__ import annotations

from typing import TypedDict, cast

from .extensions import ExtensionTransport


class GroupRetirement(TypedDict):
    roomId: str
    retired: bool


class AsyncGroupMembership:
    def __init__(self, connection: ExtensionTransport):
        self.connection = connection

    async def retire_idle(self, room_id: str, *, latest_seq: int) -> GroupRetirement:
        """Retire this exact idle revision without cancelling admitted work."""
        return cast(GroupRetirement, await self.connection.call(
            'edith.desktop.v1.groups.retire-idle', room_id=room_id,
            latest_seq=latest_seq))
