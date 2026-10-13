"""Typed bindings for EDITH's explicit, versioned native Git receipt extension."""
from __future__ import annotations

from typing import Any, Literal, TypedDict, cast

from .extensions import ExtensionTransport


class GitProviderState(TypedDict):
    installed: bool
    authenticated: bool
    hostname: str
    login: str | None
    avatarUrl: str | None
    pullRequest: dict[str, Any] | None


class GitMutationReceipt(TypedDict):
    id: str
    profileId: str
    path: str
    action: Literal['commit', 'push', 'create-pr', 'switch', 'create-branch']
    status: Literal['pending', 'applied', 'rejected', 'uncertain']
    beforeHead: str | None
    result: dict[str, Any] | None


class AsyncGitMutations:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        self.transport = transport
        self.profile = profile

    async def mutate(self, path: str, action: Literal['commit', 'push', 'create-pr', 'switch', 'create-branch'], *, request_id: str,
                     message: str | None = None, branch: str | None = None,
                     push: bool = False, include_unstaged: bool | None = None,
                     force: bool = False, refspec: str | None = None, set_upstream: bool = False, fail_if_exists: bool = True,
                     head_branch: str | None = None, base_branch: str | None = None, is_draft: bool = False,
                     title: str | None = None, body: str | None = None) -> GitMutationReceipt:
        return cast(GitMutationReceipt, await self.transport.call('edith.desktop.v1.git.mutate', timeout=120,
            profile=self.profile, path=path, action=action, request_id=request_id,
            message=message, branch=branch, push=push, includeUnstaged=include_unstaged,
            force=force, refspec=refspec, setUpstream=set_upstream, failIfExists=fail_if_exists,
            headBranch=head_branch, baseBranch=base_branch, isDraft=is_draft, title=title, body=body))

    async def operation(self, request_id: str) -> GitMutationReceipt:
        return cast(GitMutationReceipt, await self.transport.call('edith.desktop.v1.git.operation',
            profile=self.profile, request_id=request_id))

    async def provider(self, *, hostname: str = 'github.com', path: str | None = None, branch: str | None = None) -> GitProviderState:
        return cast(GitProviderState, await self.transport.call('edith.desktop.v1.git.provider',
            profile=self.profile, hostname=hostname, path=path, branch=branch))
