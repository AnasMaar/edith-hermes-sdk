"""Typed bindings for EDITH's explicit, versioned native Git receipt extension."""
from __future__ import annotations

from typing import Any, Literal, TypedDict, cast

from .extensions import ExtensionTransport


class GitMutationReceipt(TypedDict):
    id: str
    profileId: str
    path: str
    action: Literal['commit', 'push', 'create-pr', 'switch']
    status: Literal['pending', 'applied', 'uncertain']
    beforeHead: str | None
    result: dict[str, Any] | None


class AsyncGitMutations:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        self.transport = transport
        self.profile = profile

    async def mutate(self, path: str, action: Literal['commit', 'push', 'create-pr', 'switch'], *, request_id: str,
                     message: str | None = None, branch: str | None = None,
                     push: bool = False, include_unstaged: bool | None = None) -> GitMutationReceipt:
        return cast(GitMutationReceipt, await self.transport.call('edith.desktop.v1.git.mutate', timeout=120,
            profile=self.profile, path=path, action=action, request_id=request_id,
            message=message, branch=branch, push=push, includeUnstaged=include_unstaged))

    async def operation(self, request_id: str) -> GitMutationReceipt:
        return cast(GitMutationReceipt, await self.transport.call('edith.desktop.v1.git.operation',
            profile=self.profile, request_id=request_id))
