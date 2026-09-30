"""Real Kubernetes provider smoke test; uses KUBECONFIG and locally loaded images.

Run after loading edith-hermes:integration and edith-runtime-bridge:integration.
The namespace must exist. No model credentials or database are required here.
"""

from __future__ import annotations

import asyncio
import json
import uuid

import httpx
from edith_hermes_control_plane.config import Settings
from edith_hermes_control_plane.gateway import HermesGateway
from edith_hermes_control_plane.providers.kubernetes import KubernetesProvider


async def main() -> None:
    settings = Settings(
        runtime_namespace="edith-demo",
        runtime_service_account="default",
        runtime_bridge_image="edith-runtime-bridge:integration",
    )
    provider = KubernetesProvider(settings)
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
            {"demo": "sdk-smoke"},
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
        assert forward.stdout
        while True:
            line = (await asyncio.wait_for(forward.stdout.readline(), 30)).decode()
            if not line:
                raise RuntimeError("kubectl port-forward exited before readiness")
            if "Forwarding from 127.0.0.1:" in line:
                port = int(line.split("127.0.0.1:")[1].split()[0])
                break
        connection = {
            **artifact.connection,
            "transports": [{"kind": "http", "url": f"http://127.0.0.1:{port}"}],
        }
        async with httpx.AsyncClient() as probe:
            denied = await probe.post(
                f"http://127.0.0.1:{port}/rpc", json={"jsonrpc": "2.0", "id": 1, "method": "ping"}
            )
            assert denied.status_code == 401
        for name in ("Adam", "Anas"):
            result = await gateway.invoke(
                connection,
                "profiles.create",
                {"name": name, "soul": f"You are {name}'s assistant."},
            )
            assert "error" not in result
            result = await gateway.invoke(
                connection, "session.create", {"profile": name, "title": name + " Kubernetes demo"}
            )
            assert result["result"]["session_id"]
        print(
            json.dumps(
                {
                    "provider": "kubernetes",
                    "pod": identity["podName"],
                    "profiles": ["Adam", "Anas"],
                    "sessionsCreated": 2,
                    "unauthenticatedBridgeRejected": True,
                },
                indent=2,
            )
        )
    finally:
        if forward:
            forward.terminate()
            await forward.wait()
        await provider.delete(identity, retain_data=False)
        await gateway.close()
        await provider.close()
    print("Kubernetes demo workload, service, credentials and PVC deleted.")


if __name__ == "__main__":
    asyncio.run(main())
