"""Owned local desktop controllers using Hermes's native browser broker.

This explicit extension does not impersonate cloud identities or expose raw CDP.
One existing native session, profile and caller own every registration/result.
"""
from __future__ import annotations

from typing import Any, TypedDict, cast

from .extensions import ExtensionTransport


class BrowserControlSettings(TypedDict):
    enabled: bool
    revision: str
    capabilities: list[str]


class BrowserControlLease(TypedDict):
    id: str
    scope: dict[str, Any]


class AsyncBrowserControl:
    def __init__(self, connection: ExtensionTransport, profile: str = 'default'):
        self.connection, self.profile = connection, profile

    async def settings(self) -> BrowserControlSettings:
        return cast(BrowserControlSettings, await self.connection.call('edith.desktop.v1.browser-controller.settings', profile=self.profile))

    async def configure(self, *, enabled: bool, revision: str) -> BrowserControlSettings:
        return cast(BrowserControlSettings, await self.connection.call('edith.desktop.v1.browser-controller.configure', profile=self.profile, enabled=enabled, revision=revision))

    async def register(self, *, session_id: str, lease_id: str, controller_id: str,
                       browser_profile_id: str, capabilities: list[str]) -> BrowserControlLease:
        return cast(BrowserControlLease, await self.connection.call('edith.desktop.v1.browser-controller.register',
            profile=self.profile, session_id=session_id, lease_id=lease_id, controller_id=controller_id,
            browser_profile_id=browser_profile_id, capabilities=capabilities, protocol_version=1))

    async def heartbeat(self, *, session_id: str, lease_id: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.connection.call('edith.desktop.v1.browser-controller.heartbeat', profile=self.profile, session_id=session_id, lease_id=lease_id))

    async def result(self, *, session_id: str, lease_id: str, command_id: str, ok: bool,
                     result: Any = None, error: str | None = None) -> dict[str, Any]:
        return cast(dict[str, Any], await self.connection.call('edith.desktop.v1.browser-controller.result',
            profile=self.profile, session_id=session_id, lease_id=lease_id, command_id=command_id, ok=ok,
            result=result if ok else None, error=error if not ok else None))

    async def detach(self, *, session_id: str, lease_id: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.connection.call('edith.desktop.v1.browser-controller.detach', profile=self.profile, session_id=session_id, lease_id=lease_id))
