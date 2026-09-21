"""Client for the per-pod runtime bridge."""

from __future__ import annotations

from typing import Any

import httpx


class HermesGatewayError(RuntimeError):
    pass


class HermesGateway:
    def __init__(self, timeout: float = 300):
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self.client.aclose()

    async def invoke(
        self, connection: dict[str, Any], method: str, params: Any = None
    ) -> dict[str, Any]:
        http_transport = next(item for item in connection["transports"] if item["kind"] == "http")
        response = await self.client.post(
            http_transport["url"].rstrip("/") + "/rpc",
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}},
        )
        response.raise_for_status()
        value: dict[str, Any] = response.json()
        if value.get("error"):
            raise HermesGatewayError(str(value["error"]))
        return value
