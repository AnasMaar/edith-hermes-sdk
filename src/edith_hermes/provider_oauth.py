"""Profile-owned native login recovery alongside Desktop OAuth REST controls."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport


class ProviderOAuthFlow(TypedDict, total=False):
    id: str
    provider: str
    profileId: str
    sessionId: str
    status: Literal['starting', 'pending', 'approved', 'denied', 'expired', 'error', 'uncertain']
    verificationUrl: str
    userCode: str
    expiresAt: float
    pollInterval: int


class AsyncProviderOAuth:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Select a concrete provider account profile')
        self.transport, self.profile = transport, profile

    async def start(self, provider: str, *, request_id: str) -> ProviderOAuthFlow:
        return cast(ProviderOAuthFlow, await self.transport.call('edith.desktop.v1.providerOAuth.start',
            profile=self.profile, provider=provider, request_id=request_id, timeout=180))

    async def flow(self, request_id: str) -> ProviderOAuthFlow:
        return cast(ProviderOAuthFlow, await self.transport.call('edith.desktop.v1.providerOAuth.flow',
            profile=self.profile, request_id=request_id))
