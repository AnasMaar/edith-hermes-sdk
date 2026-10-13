"""Native local-model lifecycle with durable request and job ownership."""
from __future__ import annotations

from typing import Any, Literal, TypedDict, cast

from typing_extensions import NotRequired

from .extensions import ExtensionTransport

LocalModelAction = Literal['runtime-install', 'download', 'activate', 'pause', 'resume', 'remove', 'eject', 'server-start', 'server-stop']


class LocalModelReceipt(TypedDict, total=False):
    id: str
    profileId: str
    resourceId: str
    kind: LocalModelAction
    status: Literal['pending', 'running', 'paused', 'applied', 'failed', 'rejected', 'interrupted', 'uncertain']
    jobId: str
    percent: int
    canPause: bool
    canResume: bool
    phase: str
    detail: str


class LocalModelInventory(TypedDict):
    status: dict[str, Any]
    hardware: dict[str, Any]
    catalog: dict[str, Any]
    profileRevision: str
    defaultModel: str
    jobs: list[dict[str, Any]]
    hostName: NotRequired[str]


class AsyncLocalModelAdministration:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Select a concrete local-model activation profile')
        self.transport, self.profile = transport, profile

    async def inventory(self) -> LocalModelInventory:
        return cast(LocalModelInventory, await self.transport.call('edith.desktop.v1.localModels.inventory', profile=self.profile, timeout=180))

    async def change(self, kind: LocalModelAction, resource_id: str, *, request_id: str,
                     revision: str | None = None, profile_revision: str | None = None) -> LocalModelReceipt:
        return cast(LocalModelReceipt, await self.transport.call('edith.desktop.v1.localModels.change',
            profile=self.profile, kind=kind, resource_id=resource_id, request_id=request_id,
            revision=revision, profile_revision=profile_revision, timeout=180))

    async def operation(self, request_id: str) -> LocalModelReceipt:
        return cast(LocalModelReceipt, await self.transport.call('edith.desktop.v1.localModels.operation',
            profile=self.profile, request_id=request_id, timeout=180))
