"""Checked checkout handoffs and durable receipts on the owning native host."""
from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport


class CheckoutState(TypedDict):
    path: str
    repository: str
    head: str
    branch: str | None
    dirty: bool
    revision: str


class HandoffArguments(TypedDict):
    repository: str
    source: str
    target: str
    source_revision: str
    target_revision: str
    source_branch: str | None
    target_branch: str
    preserve_target: bool


class HandoffReceipt(TypedDict):
    requestId: str
    profileId: str
    repository: str
    source: str
    target: str
    status: Literal['pending', 'applied', 'uncertain']
    step: str
    recoveryRefs: dict[str, str]
    error: str | None


class HandoffBinding(TypedDict):
    sessionKey: str
    cwd: str
    requestId: str
    profileId: str


class AsyncWorktreeHandoffs:
    def __init__(self, connection: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Select the concrete profile owning this handoff')
        self.connection, self.profile = connection, profile

    async def inspect(self, repository: str, path: str) -> CheckoutState:
        return cast(CheckoutState, await self.connection.call('edith.desktop.v1.worktree_handoffs.inspect',
            profile=self.profile, repository=repository, path=path, timeout=120))

    async def mutate(self, arguments: HandoffArguments, *, request_id: str) -> HandoffReceipt:
        return cast(HandoffReceipt, await self.connection.call('edith.desktop.v1.worktree_handoffs.mutate',
            profile=self.profile, request_id=request_id, arguments=arguments, timeout=120))

    async def operation(self, repository: str, request_id: str) -> HandoffReceipt:
        return cast(HandoffReceipt, await self.connection.call('edith.desktop.v1.worktree_handoffs.operation',
            profile=self.profile, repository=repository, request_id=request_id))

    async def bind(self, repository: str, request_id: str, session_key: str) -> HandoffBinding:
        return cast(HandoffBinding, await self.connection.call('edith.desktop.v1.worktree_handoffs.bind',
            profile=self.profile, repository=repository, request_id=request_id, session_key=session_key))
