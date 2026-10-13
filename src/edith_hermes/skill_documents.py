"""Profile-owned native skill tree and supporting-file content CAS."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport, SkillDocument


class SkillFile(TypedDict):
    path: str
    name: str
    isDirectory: bool
    sizeBytes: int
    modifiedAtMs: float


class SkillFileRemoval(TypedDict):
    id: str
    resourceId: str
    path: str
    status: Literal['pending', 'applied', 'rejected', 'uncertain']


class AsyncSkillDocuments:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose the concrete profile that owns these supporting files')
        self.transport, self.profile = transport, profile

    async def list(self, skill_id: str, *, path: str = '') -> list[SkillFile]:
        result = await self.transport.call('edith.desktop.v1.skillDocuments.list', profile=self.profile, id=skill_id, path=path)
        return cast(list[SkillFile], result['entries'])

    async def read(self, skill_id: str, *, path: str) -> SkillDocument:
        return cast(SkillDocument, await self.transport.call('edith.desktop.v1.skillDocuments.read',
            profile=self.profile, id=skill_id, path=path))

    async def write(self, skill_id: str, *, path: str, revision: str, content: str) -> SkillDocument:
        return cast(SkillDocument, await self.transport.call('edith.desktop.v1.skillDocuments.write',
            profile=self.profile, id=skill_id, path=path, revision=revision, content=content))

    async def remove(self, skill_id: str, *, path: str, revision: str, request_id: str) -> SkillFileRemoval:
        return cast(SkillFileRemoval, await self.transport.call('edith.desktop.v1.skillDocuments.remove',
            profile=self.profile, id=skill_id, path=path, revision=revision, request_id=request_id))
