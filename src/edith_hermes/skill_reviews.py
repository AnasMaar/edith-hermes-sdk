"""Consent for exact native Skills Hub quarantine bytes, without a second fetch."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport, SkillActionReceipt


class SkillFinding(TypedDict):
    severity: str
    description: str


class SkillReview(TypedDict):
    id: str
    profileId: str
    resourceId: str
    policy: Literal['allow', 'ask', 'block']
    summary: str
    reason: str
    findings: list[SkillFinding]
    expiresAt: float
    bundleHash: str


class AsyncSkillReviews:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose the concrete profile that owns this review')
        self.transport, self.profile = transport, profile

    async def review(self, resource: str) -> SkillReview:
        return cast(SkillReview, await self.transport.call('edith.desktop.v1.skillReviews.review',
            profile=self.profile, resource=resource, timeout=120))

    async def install(self, resource: str, *, review_id: str, request_id: str, accepted: bool) -> SkillActionReceipt:
        return cast(SkillActionReceipt, await self.transport.call('edith.desktop.v1.skillReviews.install',
            profile=self.profile, resource=resource, review_id=review_id, request_id=request_id, accepted=accepted, timeout=120))

    async def operation(self, request_id: str) -> SkillActionReceipt:
        return cast(SkillActionReceipt, await self.transport.call('edith.desktop.v1.skillReviews.operation',
            profile=self.profile, request_id=request_id))
