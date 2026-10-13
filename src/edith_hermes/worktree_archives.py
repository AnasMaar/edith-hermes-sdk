"""Typed preservation around native Git worktree moves, separate from REST."""
from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport, WorktreeState


class ArchiveReceipt(TypedDict):
    requestId: str
    profileId: str
    archiveId: str
    kind: Literal['archive', 'restore']
    status: Literal['pending', 'applied', 'uncertain']
    originalPath: str
    archivePath: str


class AsyncWorktreeArchives:
    def __init__(self, connection: ExtensionTransport, *, profile: str):
        if not profile or profile != profile.strip() or profile.lower() == 'all':
            raise ValueError('Select a concrete profile')
        self.connection, self.profile = connection, profile

    async def inspect(self, repository: str, path: str) -> WorktreeState:
        return cast(WorktreeState, await self.connection.call(
            'edith.desktop.v1.worktree_archives.inspect', profile=self.profile,
            repository=repository, path=path))

    async def mutate(self, repository: str, path: str, *, revision: str,
                     request_id: str, kind: Literal['archive', 'restore'],
                     archive_id: str | None = None) -> ArchiveReceipt:
        return cast(ArchiveReceipt, await self.connection.call(
            'edith.desktop.v1.worktree_archives.mutate', profile=self.profile,
            repository=repository, path=path, revision=revision, request_id=request_id,
            kind=kind, archive_id=archive_id))

    async def operation(self, repository: str, request_id: str) -> ArchiveReceipt:
        return cast(ArchiveReceipt, await self.connection.call(
            'edith.desktop.v1.worktree_archives.operation', profile=self.profile,
            repository=repository, request_id=request_id))
