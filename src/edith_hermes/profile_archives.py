"""Resumable checked uploads for original native profile imports."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport
from .profile_imports import ProfileImportReview


class ProfileArchiveUpload(TypedDict):
    id: str
    profileId: str
    filename: str
    sizeBytes: int
    receivedBytes: int
    revision: str
    status: Literal['uploading', 'completed']


class AsyncProfileArchives:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose one profile that owns the archive upload')
        self.transport, self.profile = transport, profile

    async def begin(self, *, request_id: str, filename: str, size_bytes: int, revision: str) -> ProfileArchiveUpload:
        return cast(ProfileArchiveUpload, await self.transport.call('edith.desktop.v1.profileArchives.begin', profile=self.profile,
            request_id=request_id, filename=filename, size_bytes=size_bytes, revision=revision))

    async def status(self, request_id: str) -> ProfileArchiveUpload:
        return cast(ProfileArchiveUpload, await self.transport.call('edith.desktop.v1.profileArchives.status', profile=self.profile, request_id=request_id))

    async def append(self, request_id: str, *, offset: int, data_base64: str) -> ProfileArchiveUpload:
        return cast(ProfileArchiveUpload, await self.transport.call('edith.desktop.v1.profileArchives.append', profile=self.profile,
            request_id=request_id, offset=offset, data_base64=data_base64))

    async def complete(self, request_id: str) -> ProfileImportReview:
        return cast(ProfileImportReview, await self.transport.call('edith.desktop.v1.profileArchives.complete', profile=self.profile, request_id=request_id, timeout=180))
