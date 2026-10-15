"""Native curated plugin lookup and host-presence bindings.

These are not an invented catalog search API. Hermes v0.22.0 exposes lookup
by name, onboarding selections, and presence for supplied catalog names.
Installation still uses the existing reviewed plugin administration flow.
"""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from typing_extensions import NotRequired

from .connectors import CatalogAppState, _identity, _ScopedNativeRPC


class PluginCatalogEntry(TypedDict):
    name: str
    repo: str
    sha: str
    subdir: str


class PluginCatalogLookup(TypedDict):
    status: Literal["found", "invalid_name", "unknown", "unavailable"]
    entry: NotRequired[PluginCatalogEntry | None]


class CatalogPluginPresence(TypedDict):
    name: str
    title: str
    state: CatalogAppState
    sentence: str
    disclosure: str


class OnboardingCatalogPlugin(TypedDict):
    name: str
    title: str
    description: str
    tier: Literal["official", "community"]
    platforms: list[str]
    app_state: CatalogAppState
    sentence: str


class PluginCatalogPresence(TypedDict):
    presence: list[CatalogPluginPresence]


class PluginCatalogOnboarding(TypedDict):
    onboarding: list[OnboardingCatalogPlugin]


class AsyncPluginCatalog(_ScopedNativeRPC):
    async def lookup(self, name: str) -> PluginCatalogLookup:
        """Resolve the backend's current exact SHA, including its kill list.

        ``unknown`` and ``unavailable`` remain distinct outcomes. This never
        bypasses install review or falls back to an unpinned repository.
        """
        return cast(PluginCatalogLookup, await self._call("plugins.catalog.lookup", name=_identity(name, "catalog name")))

    async def presence(self, names: list[str]) -> PluginCatalogPresence:
        """Native host requirements, in requested order; unknown names omitted."""
        self._require("plugins.manage", "plugin_presence")
        return cast(PluginCatalogPresence, await self._call("plugins.manage", action="presence", names=[_identity(name, "catalog name") for name in names]))

    async def onboarding(self) -> PluginCatalogOnboarding:
        """Curated onboarding subset; this is not the complete plugin catalog."""
        return cast(PluginCatalogOnboarding, await self._call("plugins.manage", action="onboarding"))
