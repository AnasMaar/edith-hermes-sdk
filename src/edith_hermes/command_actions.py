"""Original Hermes diagnostic actions with scoped receipt/progress ownership."""
from typing import Any, Literal, TypedDict, cast

from .extensions import ExtensionTransport


class CommandActionReceipt(TypedDict, total=False):
    requestId: str
    action: Literal['doctor', 'security-audit', 'gateway-start', 'gateway-stop']
    profile: str
    status: Literal['pending', 'uncertain', 'applied', 'completed', 'failed']
    pid: int
    progress: dict[str, Any]


class AsyncCommandActions:
    def __init__(self, connection: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose the concrete profile that owns this diagnostic action')
        self.connection, self.profile = connection, profile

    async def capabilities(self) -> dict[str, list[str]]:
        return cast(dict[str, list[str]], await self.connection.call(
            'edith.desktop.v1.command-actions.capabilities', profile=self.profile))

    async def start(
        self, *, request_id: str, action: Literal['doctor', 'security-audit', 'gateway-start', 'gateway-stop']
    ) -> CommandActionReceipt:
        return cast(CommandActionReceipt, await self.connection.call(
            'edith.desktop.v1.command-actions.start', profile=self.profile,
            request_id=request_id, action=action))

    async def operation(self, request_id: str) -> CommandActionReceipt:
        return cast(CommandActionReceipt, await self.connection.call(
            'edith.desktop.v1.command-actions.operation', profile=self.profile, request_id=request_id))
