"""Profile-scoped native custom endpoints with narrow edits and durable receipts."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport

EndpointKind = Literal['save', 'remove', 'activate']
EndpointMode = Literal['', 'chat_completions', 'codex_responses', 'anthropic_messages']


class EndpointChanges(TypedDict, total=False):
    name: str
    base_url: str
    model: str
    api_key: str
    api_mode: EndpointMode
    context_length: int | None
    discover_models: bool


class CustomEndpoint(TypedDict):
    id: str
    name: str
    base_url: str
    model: str
    models: list[str]
    api_mode: EndpointMode
    context_length: int | None
    discover_models: bool
    has_api_key: bool
    is_current: bool
    source: str
    editable: bool


class EndpointInventory(TypedDict):
    profileId: str
    revision: str
    endpoints: list[CustomEndpoint]


class EndpointReceipt(TypedDict, total=False):
    id: str
    profileId: str
    resourceId: str
    kind: EndpointKind
    status: Literal['pending', 'applied', 'uncertain', 'confirmation-required']
    revision: str
    message: str


class EndpointValidation(TypedDict, total=False):
    ok: bool
    reachable: bool
    message: str
    models: list[str]
    transport_checked: str
    resolved_base_url: str


class AsyncProviderEndpoints:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose a concrete endpoint profile')
        self.transport, self.profile = transport, profile

    async def inventory(self) -> EndpointInventory:
        return cast(EndpointInventory, await self.transport.call('edith.desktop.v1.providerEndpoints.inventory', profile=self.profile))

    async def change(self, identity: str, *, revision: str, request_id: str, kind: EndpointKind, changes: EndpointChanges, confirmed: bool = False) -> EndpointReceipt:
        return cast(EndpointReceipt, await self.transport.call('edith.desktop.v1.providerEndpoints.change', profile=self.profile,
            id=identity, revision=revision, request_id=request_id, kind=kind, changes=changes, confirmed=confirmed, timeout=180))

    async def operation(self, request_id: str) -> EndpointReceipt:
        return cast(EndpointReceipt, await self.transport.call('edith.desktop.v1.providerEndpoints.operation', profile=self.profile, request_id=request_id))

    async def test(self, identity: str, changes: EndpointChanges) -> EndpointValidation:
        return cast(EndpointValidation, await self.transport.call('edith.desktop.v1.providerEndpoints.test', profile=self.profile, id=identity, changes=changes, timeout=180))
