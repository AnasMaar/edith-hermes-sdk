"""Remote and embedded transport abstractions."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4

import httpx

from .errors import error_from_response


def _python_name(value: str) -> str:
    import re

    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return value.replace("-", "_").lower()


@runtime_checkable
class AsyncTransport(Protocol):
    async def invoke(self, operation: Mapping[str, Any], arguments: Mapping[str, Any]) -> Any: ...

    def stream(
        self, operation: Mapping[str, Any], arguments: Mapping[str, Any]
    ) -> AsyncIterator[dict[str, Any]]: ...

    async def aclose(self) -> None: ...


@runtime_checkable
class EmbeddedDriver(Protocol):
    """Driver implemented by local Docker/Kubernetes or test environments."""

    async def invoke(self, operation_id: str, arguments: Mapping[str, Any]) -> Any: ...

    def stream(
        self, operation_id: str, arguments: Mapping[str, Any]
    ) -> AsyncIterator[dict[str, Any]]: ...

    async def aclose(self) -> None: ...


class EmbeddedTransport:
    def __init__(self, driver: EmbeddedDriver):
        self._driver = driver

    async def invoke(self, operation: Mapping[str, Any], arguments: Mapping[str, Any]) -> Any:
        return await self._driver.invoke(str(operation["operation_id"]), arguments)

    def stream(
        self, operation: Mapping[str, Any], arguments: Mapping[str, Any]
    ) -> AsyncIterator[dict[str, Any]]:
        return self._driver.stream(str(operation["operation_id"]), arguments)

    async def aclose(self) -> None:
        await self._driver.aclose()


class HTTPTransport:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout: float = 30.0,
        max_retries: int = 2,
        client: httpx.AsyncClient | None = None,
    ):
        self._owns_client = client is None
        self._authorization = f"Bearer {token}"
        self._max_retries = max_retries
        self._client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={"Authorization": f"Bearer {token}"},
        )

    @staticmethod
    def _request_parts(
        operation: Mapping[str, Any], arguments: Mapping[str, Any]
    ) -> tuple[str, dict[str, Any], dict[str, Any] | None, dict[str, str]]:
        path = str(operation["path"])
        remaining = dict(arguments)
        for name in operation.get("path_parameters", []):
            python_name = _python_name(str(name))
            value = remaining.pop(python_name, remaining.pop(str(name), None))
            if value is None:
                raise TypeError(f"Missing required path parameter: {python_name}")
            path = path.replace("{" + str(name) + "}", str(value))
        body = remaining.pop("body", None)
        headers = dict(remaining.pop("headers", {}) or {})
        for name in operation.get("header_parameters", []):
            python_name = _python_name(str(name))
            if python_name in remaining:
                headers[str(name)] = str(remaining.pop(python_name))
        if "Idempotency-Key" in operation.get("header_parameters", []):
            headers.setdefault("Idempotency-Key", str(uuid4()))
        query_names = set(operation.get("query_parameters", []))
        query: dict[str, Any] = {}
        for name in list(remaining):
            wire_name = next(
                (item for item in query_names if _python_name(str(item)) == name), None
            )
            if wire_name is not None:
                query[wire_name] = remaining.pop(name)
        if remaining:
            if body is not None:
                raise TypeError(f"Unexpected arguments: {sorted(remaining)}")
            body = remaining
        return path, query, body, headers

    async def invoke(self, operation: Mapping[str, Any], arguments: Mapping[str, Any]) -> Any:
        import asyncio

        path, query, body, headers = self._request_parts(operation, arguments)
        response: httpx.Response | None = None
        retryable = str(operation["method"]) in {"GET", "HEAD", "OPTIONS"} or bool(
            headers.get("Idempotency-Key")
        )
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.request(
                    str(operation["method"]),
                    path,
                    params=query,
                    json=body,
                    headers={"Authorization": self._authorization, **headers},
                )
            except httpx.TransportError:
                if not retryable or attempt == self._max_retries:
                    raise
                await asyncio.sleep(0.1 * (2**attempt))
                continue
            if response.status_code not in {429, 502, 503, 504} or not retryable:
                break
            if attempt < self._max_retries:
                await asyncio.sleep(0.1 * (2**attempt))
        assert response is not None
        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = {"title": response.reason_phrase, "detail": response.text}
            raise error_from_response(response.status_code, payload)
        if response.status_code == 204 or not response.content:
            return None
        content_type = response.headers.get("content-type", "")
        return response.json() if "json" in content_type else response.text

    async def stream(
        self, operation: Mapping[str, Any], arguments: Mapping[str, Any]
    ) -> AsyncIterator[dict[str, Any]]:
        import json

        path, query, body, headers = self._request_parts(operation, arguments)
        async with self._client.stream(
            str(operation["method"]),
            path,
            params=query,
            json=body,
            headers={"Authorization": self._authorization, **headers},
        ) as response:
            if response.status_code >= 400:
                raw = await response.aread()
                try:
                    payload = json.loads(raw)
                except (ValueError, TypeError):
                    payload = {
                        "title": response.reason_phrase,
                        "detail": raw.decode(errors="replace"),
                    }
                raise error_from_response(response.status_code, payload)
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    value = line[5:].strip()
                    yield json.loads(value) if value else {}

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
