"""Checked native context defaults with narrow field changes and durable receipts."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport

ContextValue = bool | int | float | None


class ContextField(TypedDict):
    id: str
    label: str
    description: str
    type: Literal['boolean', 'integer', 'number', 'optional-integer']
    minimum: int | float | None
    maximum: int | float | None
    value: ContextValue


class ContextInventory(TypedDict):
    profileId: str
    revision: str
    fields: list[ContextField]


class ContextReceipt(TypedDict, total=False):
    id: str
    profileId: str
    status: Literal['pending', 'applied', 'uncertain']
    revision: str
    reconciled: bool


class AsyncContextConfiguration:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose a concrete context profile')
        self.transport, self.profile = transport, profile

    async def inventory(self) -> ContextInventory:
        return cast(ContextInventory, await self.transport.call('edith.desktop.v1.contextConfiguration.inventory', profile=self.profile))

    async def change(self, *, revision: str, request_id: str, changes: dict[str, ContextValue]) -> ContextReceipt:
        return cast(ContextReceipt, await self.transport.call('edith.desktop.v1.contextConfiguration.change', profile=self.profile,
            revision=revision, request_id=request_id, changes=changes, timeout=180))

    async def operation(self, request_id: str) -> ContextReceipt:
        return cast(ContextReceipt, await self.transport.call('edith.desktop.v1.contextConfiguration.operation', profile=self.profile, request_id=request_id))
