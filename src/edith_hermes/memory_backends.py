"""Native profile memory providers, context engines and checked setup receipts."""
from __future__ import annotations

from typing import Any, Literal, TypedDict, cast

from .extensions import ExtensionTransport

MemoryBackendAction = Literal['select-memory', 'select-context', 'save', 'setup']
MemoryBackendSurface = Literal['native', 'declared']


class MemoryBackendReceipt(TypedDict):
    id: str
    profileId: str
    resourceId: str
    kind: MemoryBackendAction
    status: Literal['running', 'applied', 'failed', 'rejected', 'uncertain', 'interrupted']
    revision: str | None
    message: str | None


class AsyncMemoryBackends:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose one concrete memory backend profile')
        self.transport, self.profile = transport, profile

    async def inventory(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.transport.call('edith.desktop.v1.memoryBackends.inventory', profile=self.profile))

    async def schema(self, resource: str, *, surface: MemoryBackendSurface = 'native') -> dict[str, Any]:
        return cast(dict[str, Any], await self.transport.call('edith.desktop.v1.memoryBackends.schema', profile=self.profile, resource=resource, surface=surface))

    async def change(self, resource: str, kind: MemoryBackendAction, *, revision: str, request_id: str,
                     values: dict[str, Any] | None = None, surface: MemoryBackendSurface = 'native', confirmed: bool = False) -> MemoryBackendReceipt:
        return cast(MemoryBackendReceipt, await self.transport.call('edith.desktop.v1.memoryBackends.change', profile=self.profile,
            resource=resource, kind=kind, revision=revision, request_id=request_id, values=values or {}, surface=surface, confirmed=confirmed, timeout=180))

    async def operation(self, request_id: str) -> MemoryBackendReceipt:
        return cast(MemoryBackendReceipt, await self.transport.call('edith.desktop.v1.memoryBackends.operation', profile=self.profile, request_id=request_id))
