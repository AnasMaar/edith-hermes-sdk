"""Hermes Desktop's existing full curated plugin catalog HTTP endpoint.

Catalog metadata is deployment-wide. The native endpoint also merges its
launch-home installed state; those fields are NOT the requesting profile's
plugin inventory. Use profile-owned ``plugins.manage list`` for that inventory.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, cast

from typing_extensions import NotRequired

from .errors import RemoteError

if TYPE_CHECKING:
    from .desktop import AsyncHermesDesktop, DesktopCapabilities


class NativeCatalogCapabilities(TypedDict):
    provides_tools: list[str]
    provides_hooks: list[str]
    provides_middleware: list[str]
    requires_env: list[str]


class NativePluginCatalogEntry(TypedDict):
    name: str
    description: str
    repo: str
    sha: str
    sha_short: str
    tier: Literal["official", "community"]
    maintainer: str
    requires_hermes: str
    platforms: list[str]
    capabilities: NativeCatalogCapabilities
    docs_url: str
    capability_summary: str
    category: NotRequired[str]
    subdir: NotRequired[str]
    version: NotRequired[str]
    title: NotRequired[str]
    image: NotRequired[str]
    screenshots: NotRequired[list[str]]
    readme: NotRequired[bool]
    onboarding: NotRequired[bool]
    known_issues: NotRequired[list[str]]
    # Native launch-home annotations: never attribute these to client.profile.
    installed: bool
    installed_sha: str | None
    update_available: bool
    runtime_status: Literal["disabled", "enabled", "inactive"] | None


class NativeRemovedCatalogEntry(TypedDict):
    name: str
    repo: str
    reason: str
    date: str


class NativePluginCatalogResponse(TypedDict):
    entries: list[NativePluginCatalogEntry]
    removed: list[NativeRemovedCatalogEntry]
    generated_at: str


class DesktopPlugins:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def catalog(self, *, capabilities: DesktopCapabilities | None = None) -> NativePluginCatalogResponse:
        """Read the complete native catalog, including recalled-entry metadata.

        Discover the exact REST operation first, or supply a discovery snapshot
        from this owning deployment. Discovery/auth/network failures propagate;
        a missing operation is unsupported, not an empty catalog. This performs
        no installation and never retries a failed request.

        Although the HTTP client sends its profile, this existing native route
        does not scope installed-state annotations to that query parameter.
        Discard installed/installed_sha/update_available/runtime_status and join
        the exact profile's RPC inventory before presenting installed state.
        """
        capability = capabilities if capabilities is not None else await self.client.capabilities()
        if not capability["reachable"]:
            raise RemoteError(503, "Desktop service disconnected")
        operation = "GET /api/dashboard/plugins/catalog"
        if operation not in capability["operations"]:
            raise RemoteError(501, "Unsupported desktop operation", detail=operation)
        return cast(NativePluginCatalogResponse, await self.client._request("GET", "/api/dashboard/plugins/catalog"))
