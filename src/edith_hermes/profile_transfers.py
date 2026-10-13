"""Durable native profile backup receipts and profile-scoped archive download."""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Literal, TypedDict, cast

from .desktop import AsyncHermesDesktop
from .errors import error_from_response
from .extensions import ExtensionTransport


class ProfileExport(TypedDict, total=False):
    id: str
    profileId: str
    kind: Literal['export']
    status: Literal['pending', 'running', 'completed', 'failed', 'uncertain', 'interrupted']
    exitCode: int
    downloadable: bool
    filename: str | None


class AsyncProfileTransfers:
    def __init__(self, transport: ExtensionTransport, *, profile: str):
        if not profile or profile.strip() != profile or profile.lower() == 'all':
            raise ValueError('Choose a concrete export profile')
        self.transport, self.profile = transport, profile

    async def exports(self) -> list[ProfileExport]:
        result = await self.transport.call('edith.desktop.v1.profileTransfers.inventory', profile=self.profile)
        return cast(list[ProfileExport], result['exports'])

    async def export(self, *, request_id: str) -> ProfileExport:
        return cast(ProfileExport, await self.transport.call('edith.desktop.v1.profileTransfers.export',
            profile=self.profile, request_id=request_id, timeout=180))

    async def operation(self, request_id: str) -> ProfileExport:
        return cast(ProfileExport, await self.transport.call('edith.desktop.v1.profileTransfers.operation',
            profile=self.profile, request_id=request_id))

    async def download(self, request_id: str, desktop: AsyncHermesDesktop) -> bytes:
        return b''.join([chunk async for chunk in self.stream(request_id, desktop)])

    async def stream(self, request_id: str, desktop: AsyncHermesDesktop) -> AsyncIterator[bytes]:
        if desktop.profile != self.profile:
            raise ValueError('The download must use the exporting profile')
        record = await self.transport.call('edith.desktop.v1.profileTransfers.archive', profile=self.profile, request_id=request_id)
        async with desktop._http.stream('GET', '/api/ops/backup/download', params={'profile': self.profile, 'archive': record['archive']},
                headers={'Authorization': f'Bearer {desktop._token}'} if desktop._token else {}, timeout=180) as response:
            if response.is_error:
                await response.aread()
                raise error_from_response(response.status_code, {'detail': 'The native profile archive could not be downloaded'})
            async for chunk in response.aiter_bytes(256 * 1024):
                yield chunk
