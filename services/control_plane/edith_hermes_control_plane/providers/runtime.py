"""Runtime provider contracts and provider routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class RuntimeArtifact:
    identity: dict[str, Any]
    connection: dict[str, Any]


class RuntimeProvider(Protocol):
    kind: str

    async def start(self) -> None: ...

    async def close(self) -> None: ...

    async def provision(
        self,
        instance_id: str,
        image: str | None,
        runtime: dict[str, Any],
        labels: dict[str, str],
    ) -> RuntimeArtifact: ...

    async def scale(self, identity: dict[str, Any], replicas: int) -> None: ...

    async def delete(self, identity: dict[str, Any], retain_data: bool = False) -> None: ...

    def ready(self) -> bool: ...


class RuntimeRegistry:
    """Select a lifecycle provider from ``RuntimeSpec.kind``."""

    def __init__(self, providers: list[RuntimeProvider]):
        self.providers = {provider.kind: provider for provider in providers}

    async def start(self) -> None:
        started: list[RuntimeProvider] = []
        try:
            for provider in self.providers.values():
                await provider.start()
                started.append(provider)
        except Exception:
            for provider in reversed(started):
                await provider.close()
            raise

    async def close(self) -> None:
        for provider in reversed(list(self.providers.values())):
            await provider.close()

    def get(self, kind: str) -> RuntimeProvider:
        try:
            return self.providers[kind]
        except KeyError as exc:
            available = ", ".join(sorted(self.providers)) or "none"
            raise RuntimeError(
                f"Runtime provider {kind!r} is not enabled; enabled providers: {available}"
            ) from exc

    def for_identity(self, identity: dict[str, Any]) -> RuntimeProvider:
        provider = str(identity.get("provider", ""))
        # The public contract historically called the container provider "docker".
        return self.get("container" if provider == "docker" else provider)

    def readiness(self) -> dict[str, bool]:
        return {
            kind: bool(getattr(provider, "ready", lambda: True)())
            for kind, provider in self.providers.items()
        }

    @property
    def kinds(self) -> list[str]:
        return sorted(self.providers)
