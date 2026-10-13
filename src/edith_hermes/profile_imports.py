"""Import a reviewed native export into a fresh, parked Hermes profile."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport


class ProfileImportReview(TypedDict):
    profileId: str
    exportId: str
    revision: str
    filename: str
    sizeBytes: int
    fileCount: int
    externalUploadSupported: bool


class ProfileImportReceipt(TypedDict, total=False):
    id: str
    profileId: str
    exportId: str
    targetProfileId: str
    kind: Literal['import']
    status: Literal['pending', 'running', 'completed', 'failed', 'uncertain', 'interrupted', 'rejected']
    parked: bool
    exitCode: int


class ProfileImportInventory(TypedDict):
    profileId: str
    imports: list[ProfileImportReceipt]
    externalUploadSupported: bool


class AsyncProfileImports:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose the concrete profile that owns the export')
        self.transport, self.profile = transport, profile

    async def review(self, export_id: str) -> ProfileImportReview:
        return cast(ProfileImportReview, await self.transport.call('edith.desktop.v1.profileImports.review',
            profile=self.profile, export_id=export_id, timeout=180))

    async def inventory(self) -> ProfileImportInventory:
        return cast(ProfileImportInventory, await self.transport.call('edith.desktop.v1.profileImports.inventory', profile=self.profile))

    async def operation(self, request_id: str) -> ProfileImportReceipt:
        return cast(ProfileImportReceipt, await self.transport.call('edith.desktop.v1.profileImports.operation',
            profile=self.profile, request_id=request_id))

    async def start(self, *, request_id: str, export_id: str, revision: str, name: str) -> ProfileImportReceipt:
        return cast(ProfileImportReceipt, await self.transport.call('edith.desktop.v1.profileImports.start',
            profile=self.profile, request_id=request_id, export_id=export_id, revision=revision, name=name, timeout=180))
