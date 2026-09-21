"""Adapter-backed managed cloud runtime provider."""

from __future__ import annotations

from typing import Any

import httpx

from ..config import Settings
from .runtime import RuntimeArtifact


class NousCloudProvider:
    kind = "nous_cloud"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = httpx.AsyncClient(timeout=300)

    async def start(self) -> None:
        if not self.settings.cloud_invoke_url:
            raise RuntimeError("nous_cloud requires EDITH_CLOUD_INVOKE_URL")

    async def close(self) -> None:
        await self.client.aclose()

    def ready(self) -> bool:
        return bool(self.settings.cloud_invoke_url)

    async def _invoke(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = (
            {"Authorization": f"Bearer {self.settings.cloud_bearer_token}"}
            if self.settings.cloud_bearer_token
            else {}
        )
        response = await self.client.post(
            self.settings.cloud_invoke_url,
            headers=headers,
            json={"operation": operation, **payload},
        )
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result

    async def provision(
        self,
        instance_id: str,
        image: str | None,
        runtime: dict[str, Any],
        labels: dict[str, str],
    ) -> RuntimeArtifact:
        result = await self._invoke(
            "provision",
            {"instanceId": instance_id, "image": image, "runtime": runtime, "labels": labels},
        )
        return RuntimeArtifact(
            identity={"provider": "nous_cloud", **(result.get("identity") or {})},
            connection=result["connection"],
        )

    async def scale(self, identity: dict[str, Any], replicas: int) -> None:
        await self._invoke("scale", {"identity": identity, "replicas": replicas})

    async def delete(self, identity: dict[str, Any], retain_data: bool = False) -> None:
        await self._invoke("delete", {"identity": identity, "retainData": retain_data})
