"""Local Hermes process runtime provider."""

from __future__ import annotations

import asyncio
import os
import secrets
import socket
from pathlib import Path
from typing import Any

from ..config import Settings
from ..secrets import SecretResolver
from .runtime import RuntimeArtifact


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class ProcessProvider:
    kind = "process"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.secrets = SecretResolver(settings)
        self.processes: dict[str, asyncio.subprocess.Process] = {}

    async def start(self) -> None:
        return None

    async def close(self) -> None:
        for process in self.processes.values():
            if process.returncode is None:
                process.terminate()
        await asyncio.gather(
            *(process.wait() for process in self.processes.values()), return_exceptions=True
        )
        self.processes.clear()

    def ready(self) -> bool:
        return True

    def _environment(self, runtime: dict[str, Any]) -> dict[str, str]:
        environment = dict(os.environ)
        environment.update(self.secrets.environment(runtime))
        return environment

    async def _spawn(
        self, instance_id: str, runtime: dict[str, Any], port: int, home: str
    ) -> asyncio.subprocess.Process:
        command = list(runtime.get("command") or [])
        if command:
            executable, *arguments = command
        else:
            executable = str(runtime.get("executable") or "hermes")
            arguments = ["serve", "--host", "127.0.0.1", "--port", str(port)]
        environment = self._environment(runtime)
        environment["HERMES_HOME"] = home
        environment["HERMES_DASHBOARD_SESSION_TOKEN"] = runtime["sessionToken"]
        Path(home).mkdir(parents=True, exist_ok=True)
        # A PIPE without a reader eventually blocks a real, chatty Hermes process.
        with (Path(home) / "edith-process.log").open("ab") as log:
            process = await asyncio.create_subprocess_exec(
                executable,
                *arguments,
                env=environment,
                stdout=log,
                stderr=asyncio.subprocess.STDOUT,
            )
        self.processes[instance_id] = process
        try:
            await self._wait_port(process, port)
        except BaseException:
            if process.returncode is None:
                process.terminate()
            await process.wait()
            self.processes.pop(instance_id, None)
            raise
        return process

    async def _wait_port(
        self, process: asyncio.subprocess.Process, port: int, timeout: float = 30
    ) -> None:
        deadline = asyncio.get_running_loop().time() + timeout
        while asyncio.get_running_loop().time() < deadline:
            if process.returncode is not None:
                output = await process.stdout.read() if process.stdout else b""
                raise RuntimeError(f"Hermes process exited: {output.decode(errors='replace')}")
            try:
                _, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.close()
                await writer.wait_closed()
                return
            except OSError:
                await asyncio.sleep(0.1)
        raise TimeoutError(f"Hermes process did not listen on port {port}")

    async def provision(
        self,
        instance_id: str,
        image: str | None,
        runtime: dict[str, Any],
        labels: dict[str, str],
    ) -> RuntimeArtifact:
        del image, labels
        for item in runtime.get("volumes") or []:
            source = item.get("source") or {}
            if source.get("hostPath") != item.get("mountPath"):
                raise RuntimeError(
                    "process volumes must use an identical hostPath and mountPath; "
                    "use a container provider for filesystem remapping"
                )
        port = int(runtime.get("port") or _free_port())
        home = str(
            runtime.get("hermesHome") or Path(self.settings.local_runtime_root) / instance_id
        )
        runtime = {**runtime, "sessionToken": secrets.token_urlsafe(32)}
        process = await self._spawn(instance_id, runtime, port, home)
        return RuntimeArtifact(
            identity={
                "provider": "process",
                "processId": process.pid,
                "instanceId": instance_id,
                "port": port,
                "hermesHome": home,
                "ownsHome": not bool(runtime.get("hermesHome")),
                "runtime": runtime,
            },
            connection={
                "instanceId": instance_id,
                "transports": [{"kind": "websocket", "url": f"ws://127.0.0.1:{port}/api/ws"}],
                "authorization": {"scheme": "bearer", "token": runtime["sessionToken"]},
                "expiresAt": "9999-12-31T23:59:59Z",
            },
        )

    async def scale(self, identity: dict[str, Any], replicas: int) -> None:
        instance_id = str(identity["instanceId"])
        process = self.processes.get(instance_id)
        if replicas == 0:
            if process and process.returncode is None:
                process.terminate()
                await process.wait()
            self.processes.pop(instance_id, None)
            return
        if replicas != 1:
            raise RuntimeError("process runtimes support only scale 0 or 1")
        if process is None or process.returncode is not None:
            await self._spawn(
                instance_id,
                dict(identity["runtime"]),
                int(identity["port"]),
                str(identity["hermesHome"]),
            )

    async def delete(self, identity: dict[str, Any], retain_data: bool = False) -> None:
        await self.scale(identity, 0)
        if not retain_data and identity.get("ownsHome"):
            import shutil

            target = Path(identity["hermesHome"]).resolve()
            root = Path(self.settings.local_runtime_root).resolve()
            if target.parent != root:
                raise RuntimeError(
                    "Refusing to delete a process home outside the managed runtime root"
                )
            await asyncio.to_thread(shutil.rmtree, str(target), True)
