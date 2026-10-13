"""Explicit checked host-filesystem extension where native Desktop has no CRUD API."""
from typing import Any, Literal, Protocol, cast


class MutationRPC(Protocol):
    async def call(self, method: str, **params: Any) -> Any: ...


class AsyncFileMutations:
    def __init__(self, rpc: MutationRPC, *, profile: str):
        if not profile or profile.lower() == 'all':
            raise ValueError('Choose a concrete filesystem profile')
        self.rpc, self.profile = rpc, profile

    async def inspect(self, path: str, *, workspace_root: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.rpc.call('edith.desktop.v1.files.inspect', profile=self.profile, path=path, workspace_root=workspace_root))

    async def mutate(self, action: Literal['write', 'create-directory', 'copy', 'remove'], *, workspace_root: str, request_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return cast(dict[str, Any], await self.rpc.call('edith.desktop.v1.files.mutate', profile=self.profile, action=action, workspace_root=workspace_root, request_id=request_id, payload=payload))

    async def operation(self, request_id: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.rpc.call('edith.desktop.v1.files.operation', profile=self.profile, request_id=request_id))
