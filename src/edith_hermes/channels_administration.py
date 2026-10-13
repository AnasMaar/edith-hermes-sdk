"""Profile-owned channel configuration; credentials stay inside Hermes."""
from __future__ import annotations

from typing import Any, Literal, TypedDict, cast

from .extensions import ExtensionTransport


class ChannelChanges(TypedDict, total=False):
    enabled: bool
    env: dict[str, str]
    clear_env: list[str]


class ChannelReceipt(TypedDict, total=False):
    id: str
    resourceId: str
    profileId: str
    status: Literal['pending', 'applied', 'uncertain']
    revision: str
    hotServed: bool


class AsyncChannelAdministration:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Select a concrete messaging profile')
        self.transport, self.profile = transport, profile

    async def channels(self) -> list[dict[str, Any]]:
        result = await self.transport.call('edith.desktop.v1.channels.inventory', profile=self.profile)
        return cast(list[dict[str, Any]], result['channels'])

    async def configure(self, identity: str, *, revision: str, request_id: str,
                        changes: ChannelChanges) -> ChannelReceipt:
        return cast(ChannelReceipt, await self.transport.call('edith.desktop.v1.channels.configure',
            profile=self.profile, id=identity, revision=revision, request_id=request_id, changes=changes, timeout=180))

    async def operation(self, request_id: str) -> ChannelReceipt:
        return cast(ChannelReceipt, await self.transport.call('edith.desktop.v1.channels.operation',
            profile=self.profile, request_id=request_id))
