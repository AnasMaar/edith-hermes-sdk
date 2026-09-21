"""Root async and synchronous clients."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Callable
from typing import Any, cast

import httpx

from .generated.namespaces import (
    AsyncControlPlaneAPI,
    AsyncGatewayAPI,
    AsyncImagesAPI,
    AsyncRuntimeAPI,
    AsyncToolsAPI,
)
from .transport import AsyncTransport, EmbeddedDriver, EmbeddedTransport, HTTPTransport


class AsyncEdithHermes:
    """Canonical asynchronous EDITH Hermes client."""

    def __init__(self, transport: AsyncTransport):
        self._transport = transport
        self.images = AsyncImagesAPI(transport)
        self.control_plane = AsyncControlPlaneAPI(transport)
        self.runtime = AsyncRuntimeAPI(transport)
        self.tools = AsyncToolsAPI(transport)
        self.gateway = AsyncGatewayAPI(transport)
        # These remain generic until their external contracts are snapshotted.
        self.inference = _AsyncDynamicAPI(transport, "inference")
        self.cloud = _AsyncDynamicAPI(transport, "cloud")

    @classmethod
    def remote(
        cls,
        *,
        base_url: str,
        token: str,
        timeout: float = 30.0,
        max_retries: int = 2,
        http_client: httpx.AsyncClient | None = None,
    ) -> AsyncEdithHermes:
        return cls(
            HTTPTransport(
                base_url,
                token,
                timeout=timeout,
                max_retries=max_retries,
                client=http_client,
            )
        )

    @classmethod
    def embedded(cls, *, driver: EmbeddedDriver) -> AsyncEdithHermes:
        return cls(EmbeddedTransport(driver))

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def wait_for_image_build(
        self, build_id: str, *, timeout: float = 600.0, poll_interval: float = 1.0
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while True:
            build = await self.images.get_image_build(build_id=build_id)
            if build.get("status") in {"succeeded", "failed", "cancelled"}:
                return cast(dict[str, Any], build)
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Image build {build_id} did not finish within {timeout}s")
            await asyncio.sleep(poll_interval)

    async def wait_for_provisioning_job(
        self, job_id: str, *, timeout: float = 900.0, poll_interval: float = 1.0
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while True:
            job = await self.control_plane.get_provisioning_job(job_id=job_id)
            if job.get("phase") in {"ready", "failed", "cancelled"}:
                return cast(dict[str, Any], job)
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Provisioning job {job_id} did not finish within {timeout}s")
            await asyncio.sleep(poll_interval)

    async def __aenter__(self) -> AsyncEdithHermes:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()


class _AsyncDynamicAPI:
    def __init__(self, transport: AsyncTransport, namespace: str):
        self._transport = transport
        self._namespace = namespace

    async def invoke(self, method: str, **arguments: Any) -> Any:
        operation = {
            "operation_id": f"{self._namespace}.{method}",
            "method": "POST",
            "path": f"/v1/{self._namespace}/invoke",
            "path_parameters": [],
            "query_parameters": [],
        }
        return await self._transport.invoke(operation, {"body": {"method": method, **arguments}})


class _SyncNamespace:
    def __init__(self, target: Any):
        self._target = target

    def __getattr__(self, name: str) -> Callable[..., Any]:
        async_callable = getattr(self._target, name)

        def call(*args: Any, **kwargs: Any) -> Any:
            pending = async_callable(*args, **kwargs)
            if isinstance(pending, AsyncIterator):
                raise TypeError("Use the asynchronous client for streaming operations")
            result = asyncio.run(pending)
            if isinstance(result, AsyncIterator):
                raise TypeError("Use the asynchronous client for streaming operations")
            return result

        return call


class EdithHermes:
    """Synchronous facade. Streaming operations require AsyncEdithHermes."""

    def __init__(self, async_client: AsyncEdithHermes):
        self._async_client = async_client
        self.images = _SyncNamespace(async_client.images)
        self.control_plane = _SyncNamespace(async_client.control_plane)
        self.runtime = _SyncNamespace(async_client.runtime)
        self.tools = _SyncNamespace(async_client.tools)
        self.gateway = _SyncNamespace(async_client.gateway)
        self.inference = _SyncNamespace(async_client.inference)
        self.cloud = _SyncNamespace(async_client.cloud)

    @classmethod
    def remote(cls, **kwargs: Any) -> EdithHermes:
        return cls(AsyncEdithHermes.remote(**kwargs))

    @classmethod
    def embedded(cls, *, driver: EmbeddedDriver) -> EdithHermes:
        return cls(AsyncEdithHermes.embedded(driver=driver))

    def close(self) -> None:
        asyncio.run(self._async_client.aclose())

    def wait_for_image_build(self, build_id: str, **kwargs: Any) -> dict[str, Any]:
        return asyncio.run(self._async_client.wait_for_image_build(build_id, **kwargs))

    def wait_for_provisioning_job(self, job_id: str, **kwargs: Any) -> dict[str, Any]:
        return asyncio.run(self._async_client.wait_for_provisioning_job(job_id, **kwargs))

    def __enter__(self) -> EdithHermes:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
