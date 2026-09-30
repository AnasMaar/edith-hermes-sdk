"""Shared mechanics for contract-generated, scoped resources."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import AsyncEdithHermes


class Unset:
    """An omitted argument, distinct from an explicit JSON null."""


UNSET = Unset()


def payload(values: Mapping[str, Any], extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result = {key: value for key, value in values.items() if not isinstance(value, Unset)}
    if extra:
        duplicate = result.keys() & extra.keys()
        if duplicate:
            raise TypeError(f"Duplicate fields: {sorted(duplicate)}")
        result.update(extra)
    return result


class Resource:
    def __init__(self, sdk: AsyncEdithHermes, **scope: str):
        self._sdk = sdk
        self._scope = scope

    async def _invoke(self, operation_id: str, arguments: Mapping[str, Any]) -> Any:
        from .generated.operations import BY_ID

        return await self._sdk._transport.invoke(BY_ID[operation_id], {**self._scope, **arguments})

    def _stream(
        self, operation_id: str, arguments: Mapping[str, Any]
    ) -> AsyncIterator[dict[str, Any]]:
        from .generated.operations import BY_ID

        return self._sdk._transport.stream(BY_ID[operation_id], {**self._scope, **arguments})

    async def _native(self, method: str, params: dict[str, Any]) -> Any:
        response = await self._sdk.gateway.invoke(
            method,
            instance_id=self._scope["instance_id"],
            profile_id=self._scope["profile_id"],
            params=params,
        )
        if isinstance(response, dict) and response.get("jsonrpc") == "2.0":
            if "error" in response:
                from .errors import RemoteError

                raise RemoteError(
                    502, "Native RPC failed", body=response, detail=str(response["error"])
                )
            return response["result"]
        return response

    async def _wait(
        self,
        operation_id: str,
        field: str,
        terminal: set[str],
        *,
        timeout: float,
        poll_interval: float,
    ) -> Any:
        if timeout < 0 or poll_interval <= 0:
            raise ValueError("timeout must be nonnegative and poll_interval must be positive")
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            result = await self._invoke(operation_id, {})
            if result[field] in terminal:
                return result
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise TimeoutError(
                    f"{self._scope} is still {result[field]}; work was not cancelled"
                )
            await asyncio.sleep(min(poll_interval, remaining))
