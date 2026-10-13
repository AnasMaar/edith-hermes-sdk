"""Owned native Telegram/WhatsApp authentication flows; no client token storage."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport


class ChannelPairing(TypedDict, total=False):
    id: str
    platform: Literal['telegram', 'whatsapp']
    profileId: str
    status: Literal['installing', 'starting', 'waiting', 'ready', 'connected', 'expired', 'cancelled', 'error', 'interrupted', 'uncertain', 'applied']
    pairingId: str
    qrPayload: str
    deepLink: str
    expiresAt: float
    accountName: str
    ownerUserId: str
    restartStarted: bool
    needsRestart: bool


class AsyncChannelPairings:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose a concrete channel authentication profile')
        self.transport, self.profile = transport, profile

    async def start(self, platform: Literal['telegram', 'whatsapp'], *, request_id: str) -> ChannelPairing:
        return cast(ChannelPairing, await self.transport.call('edith.desktop.v1.channelPairings.start',
            profile=self.profile, platform=platform, request_id=request_id, timeout=180))

    async def poll(self, request_id: str) -> ChannelPairing:
        return cast(ChannelPairing, await self.transport.call('edith.desktop.v1.channelPairings.poll',
            profile=self.profile, request_id=request_id, timeout=180))

    async def cancel(self, request_id: str) -> ChannelPairing:
        return cast(ChannelPairing, await self.transport.call('edith.desktop.v1.channelPairings.cancel',
            profile=self.profile, request_id=request_id, timeout=180))

    async def apply(self, request_id: str, *, revision: str, apply_request_id: str, allowed_users: list[str]) -> ChannelPairing:
        return cast(ChannelPairing, await self.transport.call('edith.desktop.v1.channelPairings.apply',
            profile=self.profile, request_id=request_id, revision=revision, apply_request_id=apply_request_id,
            allowed_users=allowed_users, timeout=180))
