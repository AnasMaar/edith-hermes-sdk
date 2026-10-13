"""Versioned creation receipts around Hermes's native cron APIs."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .desktop import CronCreate
from .extensions import ExtensionTransport


class ScheduleCreationReceipt(TypedDict):
    requestId: str
    profileId: str
    status: Literal['pending', 'applied', 'uncertain']
    jobId: str | None


class AsyncScheduleMutations:
    def __init__(self, connection: ExtensionTransport, *, profile: str):
        self.connection, self.profile = connection, profile

    async def create(self, options: CronCreate, *, request_id: str) -> ScheduleCreationReceipt:
        """Dispatch once. A lost reply is reconciled using ``operation``."""
        return cast(ScheduleCreationReceipt, await self.connection.call(
            'edith.desktop.v1.cron.create', profile=self.profile,
            options=options, request_id=request_id, timeout=60))

    async def operation(self, request_id: str) -> ScheduleCreationReceipt:
        return cast(ScheduleCreationReceipt, await self.connection.call(
            'edith.desktop.v1.cron.creation', profile=self.profile, request_id=request_id))
