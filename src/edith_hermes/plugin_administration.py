"""Reviewed immutable native catalog actions and durable PM receipts."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport

PluginAction = Literal['install', 'update', 'remove', 'toggle']


class PluginReview(TypedDict):
    id: str
    profileId: str
    resourceId: str
    kind: PluginAction
    revision: str
    digest: str
    sha: str | None
    changes: list[str]
    expiresAt: float
    consentRequired: bool


class PluginActionReceipt(TypedDict):
    id: str
    profileId: str
    resourceId: str
    kind: PluginAction
    status: Literal['pending', 'applied', 'rejected', 'uncertain']
    revision: str | None
    restartRequired: bool
    message: str | None


class AsyncPluginAdministration:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose the concrete profile that owns this plugin action')
        self.transport, self.profile = transport, profile

    async def review(self, resource: str, kind: PluginAction, *, enabled: bool | None = None) -> PluginReview:
        return cast(PluginReview, await self.transport.call('edith.desktop.v1.pluginAdministration.review',
            profile=self.profile, resource=resource, kind=kind, enabled=enabled, timeout=120))

    async def change(self, resource: str, kind: PluginAction, *, review_id: str, digest: str,
                     request_id: str, accepted: bool, enabled: bool | None = None) -> PluginActionReceipt:
        return cast(PluginActionReceipt, await self.transport.call('edith.desktop.v1.pluginAdministration.change',
            profile=self.profile, resource=resource, kind=kind, review_id=review_id, digest=digest,
            request_id=request_id, accepted=accepted, enabled=enabled, timeout=180))

    async def operation(self, request_id: str) -> PluginActionReceipt:
        return cast(PluginActionReceipt, await self.transport.call('edith.desktop.v1.pluginAdministration.operation',
            profile=self.profile, request_id=request_id))
