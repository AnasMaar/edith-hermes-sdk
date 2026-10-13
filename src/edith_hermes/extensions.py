"""Explicit bindings for product-owned versioned extensions, separate from native RPC."""
from __future__ import annotations

from typing import Any, Protocol, TypedDict, cast


class ExtensionTransport(Protocol):
    async def call(self, method: str, *, timeout: float = 30, **params: Any) -> Any: ...


class McpPatch(TypedDict, total=False):
    command: str
    args: list[str]
    url: str
    auth: str | None
    enabled: bool
    env: dict[str, str]
    headers: dict[str, str]
    clear_environment_keys: list[str]
    clear_header_keys: list[str]


class GitInspection(TypedDict):
    root: str
    commonDir: str
    originUrl: str | None
    head: str | None
    status: dict[str, Any]
    branches: list[dict[str, Any]]


class GitObjectRequest(TypedDict):
    path: str
    objectId: str | None
    preferDisk: bool


class AsyncHermesExtensions:
    """Capabilities must be checked on the running product extension deployment."""
    def __init__(self, connection: ExtensionTransport, *, profile: str):
        if not profile or profile != profile.strip() or profile.lower() == "all":
            raise ValueError("An extension requires a concrete profile")
        self.connection, self.profile = connection, profile

    async def capabilities(self) -> dict[str, Any]:
        result = await self.connection.call("edith.desktop.v1.capabilities", profile=self.profile)
        if not isinstance(result, dict) or result.get("version") != 1:
            raise ValueError("Unsupported EDITH desktop extension version")
        return cast(dict[str, Any], result)

    async def mcp_revisions(self) -> dict[str, str]:
        result = await self.connection.call("edith.desktop.v1.mcp.revisions", profile=self.profile)
        return dict(result["revisions"])

    async def update_mcp(self, name: str, *, revision: str, patch: McpPatch, request_id: str) -> dict[str, Any]:
        """One per-server CAS update. Never replace a redacted inventory map."""
        return cast(dict[str, Any], await self.connection.call("edith.desktop.v1.mcp.update", profile=self.profile,
                                          name=name, revision=revision, patch=patch, request_id=request_id))

    async def mcp_operation(self, request_id: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.connection.call("edith.desktop.v1.mcp.operation", profile=self.profile, request_id=request_id))

    async def git_inspect(self, path: str) -> GitInspection | None:
        """Host metadata for native Git review; capability-gated versioned extension."""
        return cast(GitInspection | None, await self.connection.call("edith.desktop.v1.git.inspect", profile=self.profile, path=path))

    async def git_objects(self, path: str, requests: list[GitObjectRequest], *, limit: int = 4194304) -> list[dict[str, Any]]:
        """Bounded, read-only blob or workspace reads for native diff expansion."""
        if not 1 <= limit <= 16777216 or len(requests) > 32:
            raise ValueError("Git object reads exceed the supported bounds")
        return cast(list[dict[str, Any]], await self.connection.call("edith.desktop.v1.git.objects", profile=self.profile, path=path, requests=requests, limit=limit))
