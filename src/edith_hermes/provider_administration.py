"""Explicit checked native credential operations, separate from OAuth tokens."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport


class ProviderKey(TypedDict):
    id: str
    provider: str
    name: str
    description: str
    configured: bool
    revision: str


class ProviderKeyReceipt(TypedDict, total=False):
    id: str
    profileId: str
    resourceId: str
    kind: Literal['save', 'remove']
    status: Literal['pending', 'applied', 'uncertain']
    revision: str


class AsyncProviderAdministration:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Select a concrete provider profile')
        self.transport, self.profile = transport, profile

    async def keys(self) -> list[ProviderKey]:
        result = await self.transport.call('edith.desktop.v1.providers.keys', profile=self.profile)
        return cast(list[ProviderKey], result['keys'])

    async def save_key(self, identity: str, *, revision: str, value: str,
                       request_id: str) -> ProviderKeyReceipt:
        return cast(ProviderKeyReceipt, await self.transport.call('edith.desktop.v1.providers.changeKey',
            profile=self.profile, id=identity, revision=revision, value=value, request_id=request_id, timeout=180))

    async def remove_key(self, identity: str, *, revision: str,
                         request_id: str) -> ProviderKeyReceipt:
        return cast(ProviderKeyReceipt, await self.transport.call('edith.desktop.v1.providers.changeKey',
            profile=self.profile, id=identity, revision=revision, remove=True, request_id=request_id, timeout=180))

    async def operation(self, request_id: str) -> ProviderKeyReceipt:
        return cast(ProviderKeyReceipt, await self.transport.call('edith.desktop.v1.providers.operation',
            profile=self.profile, request_id=request_id))
