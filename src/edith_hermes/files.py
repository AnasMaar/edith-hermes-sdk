"""Versioned checked filesystem operations on the owning native Hermes host."""
from __future__ import annotations

from typing import Any, Protocol, TypedDict, cast


class FileRPC(Protocol):
    async def call(self, method: str, **params: Any) -> Any: ...


class FileSnapshot(TypedDict, total=False):
    path: str
    canonicalId: str
    revision: str
    sizeBytes: int
    modifiedAtMs: float
    createdAtMs: float | None
    contentKind: str
    isSymlink: bool
    dataBase64: str


class FileReceipt(TypedDict, total=False):
    requestId: str
    path: str
    status: str
    result: FileSnapshot
    previousRevision: str
    contentSha256: str


class AsyncFiles:
    def __init__(self, rpc: FileRPC, *, profile: str):
        if not profile or profile.lower() == 'all':
            raise ValueError('Files require a concrete owning profile')
        self.rpc, self.profile = rpc, profile

    async def capabilities(self) -> dict[str, bool]:
        return cast(dict[str, bool], await self.rpc.call('edith.desktop.v1.files.capabilities', profile=self.profile))

    async def read(self, path: str, *, include_data: bool = True) -> FileSnapshot:
        return cast(FileSnapshot, await self.rpc.call('edith.desktop.v1.files.read', profile=self.profile, path=path, include_data=include_data))

    async def save(self, path: str, *, workspace_root: str, revision: str, content: str, request_id: str) -> FileReceipt:
        return cast(FileReceipt, await self.rpc.call('edith.desktop.v1.files.save', profile=self.profile, path=path, workspace_root=workspace_root, revision=revision, content=content, request_id=request_id))

    async def operation(self, request_id: str) -> FileReceipt:
        return cast(FileReceipt, await self.rpc.call('edith.desktop.v1.files.operation', profile=self.profile, request_id=request_id))

    async def tree(self, path: str, *, workspace_root: str) -> dict[str, Any]:
        """Bounded native snapshot; rejected for unsupported SSH filesystems."""
        return cast(dict[str, Any], await self.rpc.call('edith.desktop.v1.files.tree', profile=self.profile, path=path, workspace_root=workspace_root))
