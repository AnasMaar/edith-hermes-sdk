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
    AsyncInferenceAPI,
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
        self.inference = AsyncInferenceAPI(transport)
        # Nous Portal management remains generic until its MCP contract can be vendored.
        self.cloud = _AsyncDynamicAPI(transport, "cloud")
        self._local_http: httpx.AsyncClient | None = None
        self._local_lifespan: Any = None

    @classmethod
    def remote(
        cls,
        *,
        base_url: str,
        token: str | None = None,
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

    @classmethod
    async def local(cls, *, settings: Any = None, start_worker: bool = True) -> AsyncEdithHermes:
        """Run the real control plane in-process with selectable local providers.

        Install ``edith-hermes-sdk[control-plane]`` first. The default settings use SQLite,
        anonymous local identity, and the external/process providers. Enable ``container`` in
        ``Settings.enabled_runtime_providers`` to create Docker-compatible containers.
        """
        try:
            from edith_hermes_control_plane.app import create_app
            from edith_hermes_control_plane.config import Settings
        except ImportError as exc:
            raise RuntimeError(
                "Install edith-hermes-sdk[control-plane] to use AsyncEdithHermes.local()"
            ) from exc
        effective = settings or Settings()
        app = create_app(effective, start_worker=start_worker)
        lifespan = app.router.lifespan_context(app)
        await lifespan.__aenter__()
        http = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://edith-hermes.local"
        )
        result = cls.remote(base_url="http://edith-hermes.local", http_client=http)
        result._local_http = http
        result._local_lifespan = lifespan
        return result

    async def aclose(self) -> None:
        await self._transport.aclose()
        if self._local_http is not None:
            await self._local_http.aclose()
            self._local_http = None
        if self._local_lifespan is not None:
            await self._local_lifespan.__aexit__(None, None, None)
            self._local_lifespan = None

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
    def __init__(self, target: Any, run: Callable[..., Any]):
        self._target = target
        self._run = run

    def __getattr__(self, name: str) -> Callable[..., Any]:
        async_callable = getattr(self._target, name)

        def call(*args: Any, **kwargs: Any) -> Any:
            pending = async_callable(*args, **kwargs)
            if isinstance(pending, AsyncIterator):
                raise TypeError("Use the asynchronous client for streaming operations")
            result = self._run(pending)
            if isinstance(result, AsyncIterator):
                raise TypeError("Use the asynchronous client for streaming operations")
            return result

        return call


class EdithHermes:
    """Synchronous facade. Streaming operations require AsyncEdithHermes."""

    def __init__(self, async_client: AsyncEdithHermes):
        self._async_client = async_client
        self._loop = asyncio.new_event_loop()
        self.images = _SyncNamespace(async_client.images, self._run)
        self.control_plane = _SyncNamespace(async_client.control_plane, self._run)
        self.runtime = _SyncNamespace(async_client.runtime, self._run)
        self.tools = _SyncNamespace(async_client.tools, self._run)
        self.gateway = _SyncNamespace(async_client.gateway, self._run)
        self.inference = _SyncNamespace(async_client.inference, self._run)
        self.cloud = _SyncNamespace(async_client.cloud, self._run)

    def _run(self, pending: Any) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            pending.close()
            raise RuntimeError("Use AsyncEdithHermes inside an async event loop")
        if self._loop.is_closed():
            pending.close()
            raise RuntimeError("The SDK client is closed")
        return self._loop.run_until_complete(pending)

    @classmethod
    def remote(cls, **kwargs: Any) -> EdithHermes:
        return cls(AsyncEdithHermes.remote(**kwargs))

    @classmethod
    def embedded(cls, *, driver: EmbeddedDriver) -> EdithHermes:
        return cls(AsyncEdithHermes.embedded(driver=driver))

    def close(self) -> None:
        if not self._loop.is_closed():
            self._run(self._async_client.aclose())
            self._loop.close()

    def wait_for_image_build(self, build_id: str, **kwargs: Any) -> dict[str, Any]:
        return cast(
            dict[str, Any], self._run(self._async_client.wait_for_image_build(build_id, **kwargs))
        )

    def wait_for_provisioning_job(self, job_id: str, **kwargs: Any) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            self._run(self._async_client.wait_for_provisioning_job(job_id, **kwargs)),
        )

    def __enter__(self) -> EdithHermes:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
