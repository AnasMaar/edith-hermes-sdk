"""Typed, explicit installed-skill actions; native Hub handlers own mutations."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport


class InstalledSkillReceipt(TypedDict):
    id: str
    profileId: str
    resourceId: str
    kind: Literal['update', 'uninstall']
    status: Literal['pending', 'running', 'completed', 'failed', 'uncertain']
    exitCode: int | None


class AsyncSkillAdministration:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.lower() == 'all' or profile.strip() != profile:
            raise ValueError('Select a concrete skill profile')
        self.transport, self.profile = transport, profile

    async def change(self, skill_id: str, *, revision: str,
                     kind: Literal['update', 'uninstall'], request_id: str) -> InstalledSkillReceipt:
        if kind not in {'update', 'uninstall'} or not skill_id or not revision or not request_id:
            raise ValueError('Select an installed skill, revision and action identity')
        # No mutation retry: the receipt is reconciled through skills.operation.
        return cast(InstalledSkillReceipt, await self.transport.call(
            'edith.desktop.v1.skills.checkedAction', profile=self.profile,
            id=skill_id, revision=revision, kind=kind, request_id=request_id, timeout=180))
