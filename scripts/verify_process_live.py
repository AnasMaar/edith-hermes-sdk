"""Run in an isolated Linux environment with a real Hermes executable installed."""

import asyncio
import json
import tempfile

from edith_hermes_control_plane.config import Settings
from edith_hermes_control_plane.gateway import HermesGateway
from edith_hermes_control_plane.providers.process import ProcessProvider


async def main():
    with tempfile.TemporaryDirectory(prefix="edith-process-") as root:
        provider = ProcessProvider(Settings(local_runtime_root=root))
        gateway = HermesGateway(timeout=30)
        artifact = None
        try:
            artifact = await provider.provision(
                "verification",
                None,
                {"kind": "process", "executable": "/opt/hermes/.venv/bin/hermes"},
                {},
            )
            await gateway.invoke(artifact.connection, "profiles.create", {"name": "Adam"})
            created = await gateway.invoke(
                artifact.connection, "session.create", {"profile": "Adam"}
            )
            assert created["result"]["session_id"]
            await provider.scale(artifact.identity, 0)
            await provider.scale(artifact.identity, 1)
            profiles = await gateway.invoke(artifact.connection, "profiles.list", {})
            assert "adam" in json.dumps(profiles).lower()
            print(
                json.dumps(
                    {
                        "provider": "process",
                        "platform": "Linux in isolated test container",
                        "status": "passed",
                        "authenticated_rpc": True,
                        "session_created": True,
                        "restart_persistence": True,
                    }
                ),
                flush=True,
            )
        finally:
            if artifact:
                await provider.delete(artifact.identity)
            await provider.close()
            await gateway.close()


asyncio.run(main())
