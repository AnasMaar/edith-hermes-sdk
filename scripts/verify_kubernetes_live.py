"""Real test-owned Kubernetes workload, including authenticated duplex bridge."""

from __future__ import annotations

import argparse
import asyncio
import json
import uuid

import httpx
from edith_hermes_control_plane.config import Settings
from edith_hermes_control_plane.gateway import HermesGateway
from edith_hermes_control_plane.providers.kubernetes import KubernetesProvider

from edith_hermes.duplex import NativeConnection


async def main(bridge_image: str):
    provider = KubernetesProvider(
        Settings(
            runtime_namespace="edith-demo",
            runtime_service_account="default",
            runtime_bridge_image=bridge_image,
        )
    )
    gateway = HermesGateway()
    instance_id = "instance_" + uuid.uuid4().hex
    identity = {
        "namespace": "edith-demo",
        "workloadName": "hermes-" + instance_id.replace("_", "-"),
    }
    forward = None
    await provider.start()
    try:
        artifact = await provider.provision(
            instance_id,
            "edith-hermes:integration",
            {
                "kind": "kubernetes",
                "resources": {"cpu": "1", "memory": "2Gi"},
            },
            {"verification": "sdk-live"},
        )
        identity = artifact.identity
        forward = await asyncio.create_subprocess_exec(
            "kubectl",
            "-n",
            "edith-demo",
            "port-forward",
            "service/" + identity["workloadName"],
            ":8081",
            "--address=127.0.0.1",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        while True:
            line = (await asyncio.wait_for(forward.stdout.readline(), 30)).decode()
            if not line:
                raise RuntimeError("Port forwarding stopped")
            if "Forwarding from 127.0.0.1:" in line:
                port = int(line.split("127.0.0.1:")[1].split()[0])
                break
        url = f"http://127.0.0.1:{port}"
        connection = {**artifact.connection, "transports": [{"kind": "http", "url": url}]}
        async with httpx.AsyncClient() as client:
            assert (
                await client.post(url + "/rpc", json={"jsonrpc": "2.0", "id": 1, "method": "ping"})
            ).status_code == 401
        for name in ("Adam", "Anas"):
            await gateway.invoke(connection, "profiles.create", {"name": name})
            session = await gateway.invoke(
                connection, "session.create", {"profile": name, "title": "live verification"}
            )
            assert session["result"]["session_id"]
        socket = await gateway._connect(connection)
        duplex = NativeConnection(socket, profile="Adam")
        try:
            await duplex.call("client.capabilities", server_requests=True)
            assert await duplex.call("ping") is not None
            assert (await duplex.call("session.create"))["session_id"]
        finally:
            await duplex.aclose()
        print(
            json.dumps(
                {
                    "provider": "kubernetes",
                    "status": "passed",
                    "profiles": 2,
                    "sessions": 3,
                    "unauthenticated_bridge_rejected": True,
                    "persistent_bridge_rpc": True,
                }
            ),
            flush=True,
        )
    finally:
        if forward:
            forward.terminate()
            await forward.wait()
        await provider.delete(identity, retain_data=False)
        await gateway.close()
        await provider.close()
    print("Test workload, service, secret and PVC removed.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bridge-image", default="edith-runtime-bridge:integration")
    asyncio.run(main(parser.parse_args().bridge_image))
