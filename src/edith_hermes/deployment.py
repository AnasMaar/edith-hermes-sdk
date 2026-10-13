"""Read Hermes's native stable per-install identity without inventing a host ID."""
from __future__ import annotations

import re
from typing import TypedDict

from .desktop import AsyncHermesDesktop


class DeploymentIdentity(TypedDict):
    installId: str


class AsyncDeployment:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def identity(self) -> DeploymentIdentity:
        status = await self.client._request('GET', '/api/status')
        identity = status.get('install_id') if isinstance(status, dict) else None
        if not isinstance(identity, str) or not re.fullmatch(r'[0-9a-f]{32}', identity):
            raise ValueError('The deployment does not publish a persistent Hermes installation identity')
        return {'installId': identity}
