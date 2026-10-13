"""Versioned creation receipts around Hermes's native cron APIs."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .desktop import CronCreate, CronJob
from .extensions import ExtensionTransport


class ScheduleCreationReceipt(TypedDict):
    requestId: str
    profileId: str
    status: Literal['pending', 'applied', 'uncertain']
    jobId: str | None


class ScheduleEditReceipt(TypedDict):
    requestId: str
    profileId: str
    jobId: str
    revision: str
    status: Literal['pending', 'applied', 'uncertain', 'rejected', 'conflict']


class ScheduleSnapshot(TypedDict):
    job: CronJob
    revision: str


class ScheduleChanges(TypedDict, total=False):
    name: str
    prompt: str
    schedule: str
    enabled: bool
    deliver: str


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

    async def snapshot(self) -> list[ScheduleSnapshot]:
        """Read full native jobs and their revisions in one storage lock."""
        result = await self.connection.call('edith.desktop.v1.cron.snapshot', profile=self.profile)
        return cast(list[ScheduleSnapshot], result['jobs'])

    async def edit(self, job_id: str, *, revision: str, updates: ScheduleChanges, request_id: str) -> ScheduleEditReceipt:
        """Compare and save once using the native cron editor. Replays never write."""
        return cast(ScheduleEditReceipt, await self.connection.call(
            'edith.desktop.v1.cron.edit', profile=self.profile, job_id=job_id,
            revision=revision, updates=updates, request_id=request_id, timeout=60))

    async def edit_operation(self, request_id: str) -> ScheduleEditReceipt:
        return cast(ScheduleEditReceipt, await self.connection.call(
            'edith.desktop.v1.cron.editOperation', profile=self.profile, request_id=request_id))
