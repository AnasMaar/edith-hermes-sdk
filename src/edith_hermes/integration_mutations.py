"""Typed revision-checked integration mutations, separate from native RPC."""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .extensions import ExtensionTransport


class IntegrationReceipt(TypedDict):
    requestId: str
    name: str
    status: Literal['pending', 'applied', 'rejected', 'conflict', 'uncertain']
    revision: str


class AsyncIntegrationMutations:
    def __init__(self, connection: ExtensionTransport, *, profile: str):
        self.connection, self.profile = connection, profile

    async def remove_mcp(self, name: str, *, revision: str, request_id: str) -> IntegrationReceipt:
        """Dispatch once. On a lost reply, read the same operation receipt."""
        return cast(IntegrationReceipt, await self.connection.call(
            'edith.desktop.v1.mcp.remove', profile=self.profile, name=name,
            revision=revision, request_id=request_id))

    async def operation(self, request_id: str) -> IntegrationReceipt:
        return cast(IntegrationReceipt, await self.connection.call(
            'edith.desktop.v1.mcp.operation', profile=self.profile, request_id=request_id))
