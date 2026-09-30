from __future__ import annotations

import socket
import sys
import types
from pathlib import Path
from typing import Any

import pytest
import respx
from edith_hermes_control_plane.config import Settings
from edith_hermes_control_plane.providers import (
    DockerProvider,
    ExternalProvider,
    NousCloudProvider,
    ProcessProvider,
)
from httpx import Response


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


@pytest.mark.asyncio
async def test_process_provider_owns_local_lifecycle(tmp_path: Path) -> None:
    port = free_port()
    code = (
        "import socket,time;"
        "s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);"
        f"s.bind(('127.0.0.1',{port}));s.listen();time.sleep(120)"
    )
    provider = ProcessProvider(Settings(local_runtime_root=str(tmp_path)))
    artifact = await provider.provision(
        "instance_process",
        None,
        {
            "kind": "process",
            "port": port,
            "command": [sys.executable, "-c", code],
        },
        {},
    )
    assert artifact.identity["provider"] == "process"
    assert artifact.connection["transports"][0]["kind"] == "websocket"
    authorization = artifact.connection["authorization"]
    assert authorization["scheme"] == "bearer"
    assert len(authorization["token"]) >= 32
    assert artifact.identity["runtime"]["sessionToken"] == authorization["token"]
    assert (Path(artifact.identity["hermesHome"]) / "edith-process.log").is_file()
    await provider.scale(artifact.identity, 0)
    await provider.scale(artifact.identity, 1)
    await provider.delete(artifact.identity)
    await provider.close()


class NotFound(Exception):
    pass


class FakeContainer:
    def __init__(self) -> None:
        self.id = "container-id"
        self.attrs = {"NetworkSettings": {"Ports": {"9119/tcp": [{"HostPort": "49119"}]}}}
        self.actions: list[str] = []

    def reload(self) -> None:
        self.actions.append("reload")

    def stop(self) -> None:
        self.actions.append("stop")

    def start(self) -> None:
        self.actions.append("start")

    def remove(self, **_: Any) -> None:
        self.actions.append("remove")


class FakeContainers:
    def __init__(self, container: FakeContainer) -> None:
        self.container = container
        self.created = False
        self.last_kwargs: dict[str, Any] = {}

    def get(self, _: str) -> FakeContainer:
        if not self.created:
            raise NotFound
        return self.container

    def run(self, _: str, **kwargs: Any) -> FakeContainer:
        self.created = True
        self.last_kwargs = kwargs
        return self.container


class FakeDockerClient:
    def __init__(self) -> None:
        self.container = FakeContainer()
        self.containers = FakeContainers(self.container)
        self.removed_volumes: list[str] = []
        self.volumes = types.SimpleNamespace(
            get=lambda name: types.SimpleNamespace(remove=lambda: self.removed_volumes.append(name))
        )

    def ping(self) -> bool:
        return True

    def close(self) -> None:
        return None


@pytest.mark.asyncio
async def test_container_provider_owns_docker_lifecycle(monkeypatch: pytest.MonkeyPatch) -> None:
    client = FakeDockerClient()
    monkeypatch.setitem(sys.modules, "docker", types.SimpleNamespace(from_env=lambda: client))
    monkeypatch.setenv("EDITH_SECRET_PROVIDER_KEY", "secret-value")
    provider = DockerProvider(Settings())
    await provider.start()
    artifact = await provider.provision(
        "instance_container",
        "nousresearch/hermes-agent:latest",
        {
            "kind": "container",
            "skipReadinessCheck": True,
            "resources": {"cpu": "500m", "memory": "1Gi"},
            "environment": {"PROVIDER_KEY": {"secretRef": {"name": "provider", "key": "key"}}},
        },
        {},
    )
    assert artifact.identity["provider"] == "container"
    assert client.containers.last_kwargs["environment"]["PROVIDER_KEY"] == "secret-value"
    assert client.containers.last_kwargs["nano_cpus"] == 500_000_000
    await provider.scale(artifact.identity, 0)
    await provider.scale(artifact.identity, 1)
    await provider.delete(artifact.identity)
    assert client.container.actions[-4:] == ["stop", "start", "reload", "remove"]
    assert client.removed_volumes == ["edith-hermes-instance-container-data"]
    await provider.close()


@pytest.mark.asyncio
async def test_external_provider_adopts_without_owning_lifecycle() -> None:
    provider = ExternalProvider()
    artifact = await provider.provision(
        "instance_external",
        None,
        {"kind": "external", "endpoint": "https://hermes.example/bridge"},
        {},
    )
    assert artifact.identity["provider"] == "external"
    assert artifact.connection["transports"][0]["kind"] == "http"
    await provider.scale(artifact.identity, 0)
    await provider.delete(artifact.identity)


@pytest.mark.asyncio
@respx.mock
async def test_cloud_provider_delegates_lifecycle_to_configured_adapter() -> None:
    route = respx.post("https://cloud.example/invoke").mock(
        side_effect=[
            Response(
                200,
                json={
                    "identity": {"remoteId": "remote-1"},
                    "connection": {
                        "instanceId": "instance_cloud",
                        "transports": [{"kind": "websocket", "url": "wss://cloud.example/api/ws"}],
                        "expiresAt": "9999-12-31T23:59:59Z",
                    },
                },
            ),
            Response(200, json={}),
            Response(200, json={}),
        ]
    )
    provider = NousCloudProvider(
        Settings(
            cloud_invoke_url="https://cloud.example/invoke",
            cloud_bearer_token="cloud-token",
        )
    )
    await provider.start()
    artifact = await provider.provision(
        "instance_cloud", None, {"kind": "nous_cloud", "cloud": {}}, {}
    )
    assert artifact.identity == {"provider": "nous_cloud", "remoteId": "remote-1"}
    await provider.scale(artifact.identity, 0)
    await provider.delete(artifact.identity)
    assert route.call_count == 3
    assert route.calls[0].request.headers["authorization"] == "Bearer cloud-token"
    await provider.close()
