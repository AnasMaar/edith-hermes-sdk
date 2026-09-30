"""Docker-compatible local container runtime provider."""

from __future__ import annotations

import asyncio
import re
import secrets
from typing import Any

import httpx

from ..config import Settings
from ..secrets import SecretResolver
from .runtime import RuntimeArtifact


class DockerProvider:
    kind = "container"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.secrets = SecretResolver(settings)
        self.client: Any = None

    async def start(self) -> None:
        try:
            import docker
        except ImportError as exc:
            raise RuntimeError(
                "Install edith-hermes-sdk[embedded] to use container runtimes"
            ) from exc
        self.client = await asyncio.to_thread(docker.from_env)
        await asyncio.to_thread(self.client.ping)

    async def close(self) -> None:
        if self.client is not None:
            await asyncio.to_thread(self.client.close)
            self.client = None

    def ready(self) -> bool:
        return self.client is not None

    @staticmethod
    async def _wait_port(port: int, timeout: float = 60) -> None:
        deadline = asyncio.get_running_loop().time() + timeout
        while asyncio.get_running_loop().time() < deadline:
            try:
                _, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.close()
                await writer.wait_closed()
                return
            except OSError:
                await asyncio.sleep(0.2)
        raise TimeoutError(f"Hermes container did not listen on port {port}")

    def _environment(self, runtime: dict[str, Any]) -> dict[str, str]:
        values = {"HERMES_HOME": "/opt/data", **self.secrets.environment(runtime)}
        return values

    @staticmethod
    async def _wait_dashboard(port: int) -> None:
        async with httpx.AsyncClient(timeout=2) as probe:
            for _ in range(120):
                try:
                    response = await probe.get(f"http://127.0.0.1:{port}/api/auth/providers")
                    if response.status_code == 200:
                        return
                except httpx.HTTPError:
                    pass
                await asyncio.sleep(1)
        raise TimeoutError("Hermes dashboard did not become ready within 120 seconds")

    @staticmethod
    def _cpu(value: Any) -> int:
        text = str(value)
        cores = float(text[:-1]) / 1000 if text.endswith("m") else float(text)
        return int(cores * 1_000_000_000)

    @staticmethod
    def _memory(value: Any) -> int:
        """Normalize Kubernetes quantities and Docker units to bytes."""
        match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([KMGTPEkmgtpe]?)(i?[bB]?)", str(value))
        if match is None:
            raise ValueError(f"Invalid memory quantity: {value!r}")
        amount, unit, suffix = match.groups()
        exponent = "KMGTPE".index(unit.upper()) + 1 if unit else 0
        base = 1024 if "i" in suffix or unit.islower() else 1000
        return int(float(amount) * base**exponent)

    @staticmethod
    def _volumes(instance_id: str, runtime: dict[str, Any]) -> dict[str, dict[str, str]]:
        volumes: dict[str, dict[str, str]] = {
            f"edith-hermes-{instance_id.replace('_', '-')}-data": {
                "bind": "/opt/data",
                "mode": "rw",
            }
        }
        for item in runtime.get("volumes") or []:
            source = item.get("source") or {}
            if source.get("hostPath"):
                origin = str(source["hostPath"])
            elif source.get("persistentVolumeClaim"):
                origin = str(source["persistentVolumeClaim"])
            elif source.get("emptyDir"):
                origin = f"edith-hermes-{instance_id}-{item['name']}"
            else:
                raise RuntimeError(f"Volume {item.get('name')} has no supported source")
            volumes[origin] = {
                "bind": str(item["mountPath"]),
                "mode": "ro" if item.get("readOnly") else "rw",
            }
        return volumes

    async def provision(
        self,
        instance_id: str,
        image: str | None,
        runtime: dict[str, Any],
        labels: dict[str, str],
    ) -> RuntimeArtifact:
        if self.client is None:
            raise RuntimeError("Container provider is not started")
        image = image or runtime.get("image")
        if not image:
            raise RuntimeError("container runtimes require runtime.image or managedImageId")
        name = "edith-hermes-" + instance_id.replace("_", "-")
        try:
            existing = await asyncio.to_thread(self.client.containers.get, name)
            await asyncio.to_thread(existing.remove, force=True)
        except Exception as exc:
            if exc.__class__.__name__ != "NotFound":
                raise
        resources = runtime.get("resources") or {}
        environment = self._environment(runtime)
        password = environment.setdefault(
            "HERMES_DASHBOARD_BASIC_AUTH_PASSWORD", secrets.token_urlsafe(32)
        )
        username = environment.setdefault("HERMES_DASHBOARD_BASIC_AUTH_USERNAME", "edith")
        kwargs: dict[str, Any] = {
            "name": name,
            "detach": True,
            "command": runtime.get("command")
            or ["serve", "--host", "0.0.0.0", "--port", str(self.settings.gateway_port)],
            "environment": environment,
            "labels": {**labels, "edith.instance-id": instance_id},
            "ports": {f"{self.settings.gateway_port}/tcp": ("127.0.0.1", None)},
            "volumes": self._volumes(instance_id, runtime),
            "restart_policy": {"Name": "unless-stopped"},
            "extra_hosts": runtime.get("extraHosts") or {"host.docker.internal": "host-gateway"},
        }
        if resources.get("memory"):
            kwargs["mem_limit"] = self._memory(resources["memory"])
        if resources.get("cpu"):
            kwargs["nano_cpus"] = self._cpu(resources["cpu"])
        if resources.get("gpu"):
            try:
                import docker

                kwargs["device_requests"] = [
                    docker.types.DeviceRequest(count=int(resources["gpu"]), capabilities=[["gpu"]])
                ]
            except (ImportError, AttributeError) as exc:
                raise RuntimeError(
                    "The Docker engine/client does not support GPU requests"
                ) from exc
        container = await asyncio.to_thread(self.client.containers.run, image, **kwargs)
        ports = None
        for _ in range(100):
            await asyncio.to_thread(container.reload)
            ports = container.attrs["NetworkSettings"]["Ports"].get(
                f"{self.settings.gateway_port}/tcp"
            )
            if ports:
                break
            await asyncio.sleep(0.1)
        if not ports:
            await asyncio.to_thread(container.remove, force=True)
            raise RuntimeError("Docker did not publish the Hermes gateway port")
        host_port = int(ports[0]["HostPort"])
        if not runtime.get("skipReadinessCheck", False):
            try:
                await self._wait_dashboard(host_port)
            except BaseException:
                await asyncio.to_thread(container.remove, force=True)
                raise
        return RuntimeArtifact(
            identity={
                "provider": "container",
                "containerId": container.id,
                "containerName": name,
                "image": image,
                "imageDigest": image.rsplit("@", 1)[1] if "@" in image else None,
                "port": host_port,
                "skipReadinessCheck": runtime.get("skipReadinessCheck", False),
                "ownedDataVolume": f"edith-hermes-{instance_id.replace('_', '-')}-data",
            },
            connection={
                "instanceId": instance_id,
                "transports": [
                    {
                        "kind": "websocket",
                        "url": f"ws://127.0.0.1:{host_port}/api/ws",
                    }
                ],
                "authorization": {
                    "scheme": "dashboard_password",
                    "username": username,
                    "password": password,
                },
                "expiresAt": "9999-12-31T23:59:59Z",
            },
        )

    async def _container(self, identity: dict[str, Any]) -> Any:
        if self.client is None:
            raise RuntimeError("Container provider is not started")
        return await asyncio.to_thread(self.client.containers.get, identity["containerId"])

    async def scale(self, identity: dict[str, Any], replicas: int) -> None:
        container = await self._container(identity)
        if replicas == 0:
            await asyncio.to_thread(container.stop)
        elif replicas == 1:
            await asyncio.to_thread(container.start)
            ports = None
            for _ in range(100):
                await asyncio.to_thread(container.reload)
                ports = container.attrs["NetworkSettings"]["Ports"].get(
                    f"{self.settings.gateway_port}/tcp"
                )
                if ports:
                    break
                await asyncio.sleep(0.1)
            if not ports:
                raise RuntimeError(
                    "Docker did not republish the Hermes gateway port after starting"
                )
            identity["port"] = int(ports[0]["HostPort"])
            if not identity.get("skipReadinessCheck"):
                await self._wait_dashboard(identity["port"])
        else:
            raise RuntimeError("container runtimes support only scale 0 or 1")

    async def delete(self, identity: dict[str, Any], retain_data: bool = False) -> None:
        container = await self._container(identity)
        await asyncio.to_thread(container.remove, force=True, v=not retain_data)
        if not retain_data and identity.get("ownedDataVolume"):
            volume = await asyncio.to_thread(self.client.volumes.get, identity["ownedDataVolume"])
            await asyncio.to_thread(volume.remove)
