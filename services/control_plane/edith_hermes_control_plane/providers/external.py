"""Provider for an already-running Hermes gateway or runtime bridge."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from .runtime import RuntimeArtifact


class ExternalProvider:
    kind = "external"

    async def start(self) -> None:
        return None

    async def close(self) -> None:
        return None

    def ready(self) -> bool:
        return True

    async def provision(
        self,
        instance_id: str,
        image: str | None,
        runtime: dict[str, Any],
        labels: dict[str, str],
    ) -> RuntimeArtifact:
        del image, labels
        endpoint = str(runtime.get("endpoint") or "")
        parsed = urlparse(endpoint)
        if parsed.scheme not in {"http", "https", "ws", "wss"} or not parsed.netloc:
            raise RuntimeError("external runtimes require an http(s) or ws(s) runtime.endpoint")
        transport = "websocket" if parsed.scheme.startswith("ws") else "http"
        connection = {
            "instanceId": instance_id,
            "transports": [{"kind": transport, "url": endpoint}],
            "authorization": runtime.get("authorization") or {"scheme": "none"},
            "expiresAt": "9999-12-31T23:59:59Z",
        }
        return RuntimeArtifact(
            identity={"provider": "external", "endpoint": endpoint}, connection=connection
        )

    async def scale(self, identity: dict[str, Any], replicas: int) -> None:
        del identity
        if replicas not in {0, 1}:
            raise RuntimeError("external runtimes support only logical scale 0 or 1")

    async def delete(self, identity: dict[str, Any], retain_data: bool = False) -> None:
        del identity, retain_data
