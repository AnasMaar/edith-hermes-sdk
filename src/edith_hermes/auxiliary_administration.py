"""Native task model defaults with checked revisions and action receipts."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport


class AuxiliaryTask(TypedDict, total=False):
    task: str
    provider: str
    model: str
    reasoning_effort: str | None
    base_url: str
    local_endpoint: bool
    label: str
    hint: str
    plugin: str
    inherit_from: str | None
    effective: dict[str, str]
    revision: str


class AuxiliaryReceipt(TypedDict, total=False):
    id: str
    profileId: str
    resourceId: str
    status: Literal['pending', 'applied', 'uncertain', 'confirmation-required']
    message: str
    revision: str


class AsyncAuxiliaryAdministration:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Select a concrete auxiliary model profile')
        self.transport, self.profile = transport, profile

    async def tasks(self) -> list[AuxiliaryTask]:
        result = await self.transport.call('edith.desktop.v1.auxiliary.list', profile=self.profile)
        return cast(list[AuxiliaryTask], result['tasks'])

    async def change(self, task: str, *, revision: str, request_id: str,
                     provider: str, model: str, effort: str | None,
                     confirmed: bool = False) -> AuxiliaryReceipt:
        return cast(AuxiliaryReceipt, await self.transport.call('edith.desktop.v1.auxiliary.change',
            profile=self.profile, task=task, revision=revision, request_id=request_id,
            provider=provider, model=model, effort=effort, confirmed=confirmed, timeout=180))

    async def operation(self, request_id: str) -> AuxiliaryReceipt:
        return cast(AuxiliaryReceipt, await self.transport.call('edith.desktop.v1.auxiliary.operation',
            profile=self.profile, request_id=request_id))
