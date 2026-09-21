from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Any

import pytest

from edith_hermes import AsyncEdithHermes


class RecordingDriver:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Mapping[str, Any]]] = []

    async def invoke(self, operation_id: str, arguments: Mapping[str, Any]) -> Any:
        self.calls.append((operation_id, arguments))
        return {"operationId": operation_id}

    async def stream(
        self, operation_id: str, arguments: Mapping[str, Any]
    ) -> AsyncIterator[dict[str, Any]]:
        yield {"operationId": operation_id}

    async def aclose(self) -> None:
        return None


@pytest.mark.asyncio
async def test_embedded_driver_uses_same_namespace() -> None:
    driver = RecordingDriver()
    sdk = AsyncEdithHermes.embedded(driver=driver)
    result = await sdk.control_plane.list_instances(status="ready")
    assert result == {"operationId": "listInstances"}
    assert driver.calls[0][0] == "listInstances"
    await sdk.aclose()
