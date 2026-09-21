"""Create one Docker Hermes instance with isolated Adam and Anas profiles and tools.

Requirements:
    uv sync --extra control-plane
    Docker Desktop / Docker Engine running

Run:
    uv run python examples/docker_two_profiles.py
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import uuid
from pathlib import Path
from typing import Any

import uvicorn
from edith_hermes_control_plane.app import create_app
from edith_hermes_control_plane.config import Settings
from fastapi import FastAPI

from edith_hermes import AsyncEdithHermes

OWNER = {"tenantId": "local", "subjectId": "demo-user"}
NOTES: list[str] = []


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def tool_result(call_id: str, value: Any) -> dict[str, Any]:
    return {
        "callId": call_id,
        "isError": False,
        "content": [{"type": "json", "data": value}],
        "structuredContent": value,
    }


tool_host = FastAPI(title="Adam and Anas demo tools")


@tool_host.post("/adam")
async def adam_tools(call: dict[str, Any]) -> dict[str, Any]:
    arguments = call.get("arguments") or {}
    if call["tool"] == "adam.get_weather":
        city = arguments.get("city", "Casablanca")
        return tool_result(
            call["callId"],
            {"city": city, "condition": "sunny", "temperatureC": 24},
        )
    if call["tool"] == "adam.celsius_to_fahrenheit":
        celsius = float(arguments["celsius"])
        return tool_result(call["callId"], {"celsius": celsius, "fahrenheit": celsius * 1.8 + 32})
    return {
        "callId": call["callId"],
        "isError": True,
        "content": [{"type": "text", "text": "Unknown Adam tool"}],
    }


@tool_host.post("/anas")
async def anas_tools(call: dict[str, Any]) -> dict[str, Any]:
    arguments = call.get("arguments") or {}
    if call["tool"] == "anas.save_note":
        NOTES.append(str(arguments["text"]))
        return tool_result(call["callId"], {"saved": True, "noteCount": len(NOTES)})
    if call["tool"] == "anas.list_notes":
        return tool_result(call["callId"], {"notes": list(NOTES)})
    return {
        "callId": call["callId"],
        "isError": True,
        "content": [{"type": "text", "text": "Unknown Anas tool"}],
    }


async def start_server(app: FastAPI, port: int) -> tuple[uvicorn.Server, asyncio.Task[None]]:
    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=port, log_level="warning", access_log=False)
    )
    task = asyncio.create_task(server.serve())
    for _ in range(300):
        if server.started:
            return server, task
        if task.done():
            await task
        await asyncio.sleep(0.1)
    server.should_exit = True
    raise TimeoutError(f"Server on port {port} did not start")


def definition(
    name: str, description: str, properties: dict[str, Any], required: list[str]
) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
    }


async def main() -> None:
    tool_port = free_port()
    control_port = free_port()
    data = Path(".demo")
    data.mkdir(exist_ok=True)

    tool_server, tool_task = await start_server(tool_host, tool_port)
    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{(data / 'two-profiles.db').resolve()}",
        auth_mode="none",
        anonymous_tenant_id=OWNER["tenantId"],
        anonymous_subject_id=OWNER["subjectId"],
        enabled_runtime_providers=["container"],
        public_base_url=f"http://host.docker.internal:{control_port}",
        worker_poll_seconds=0.1,
        worker_concurrency=2,
    )
    control_server: uvicorn.Server | None = None
    control_task: asyncio.Task[None] | None = None
    sdk: AsyncEdithHermes | None = None
    instance_id: str | None = None
    try:
        control_server, control_task = await start_server(create_app(settings), control_port)
        sdk = AsyncEdithHermes.remote(base_url=f"http://127.0.0.1:{control_port}")

        capabilities = await sdk.control_plane.get_control_plane_capabilities()
        print("\nControl-plane capabilities:\n" + json.dumps(capabilities, indent=2))

        job = await sdk.control_plane.provision_user_instance(
            body={
                "owner": OWNER,
                "name": "adam-and-anas-hermes",
                "runtime": {
                    "kind": "container",
                    "image": os.getenv("HERMES_IMAGE", "nousresearch/hermes-agent:latest"),
                    "resources": {"cpu": "1", "memory": "2Gi"},
                    "environment": {},
                },
                "bootstrap": {
                    "profile": {
                        "name": "Adam",
                        "description": "Adam's isolated assistant profile",
                        "soul": "You are Adam's concise personal assistant.",
                    }
                },
                "labels": {"demo": "two-profiles"},
            }
        )
        ready = await sdk.wait_for_provisioning_job(job["id"], timeout=300)
        if ready["phase"] != "ready":
            raise RuntimeError(json.dumps(ready.get("error"), indent=2))
        instance_id = ready["instanceId"]
        adam_profile_id = ready["profileId"]

        anas = await sdk.control_plane.create_profile(
            instance_id=instance_id,
            body={
                "name": "Anas",
                "description": "Anas's isolated builder profile",
                "soul": "You are Anas's engineering copilot. Prefer concrete implementation.",
            },
        )

        adam_bundle = await sdk.tools.create_tool_bundle(
            body={
                "name": "adam-personal-tools",
                "description": "Weather and temperature utilities available only to Adam",
                "transport": "callback",
                "callback": {"url": f"http://127.0.0.1:{tool_port}/adam"},
                "tools": [
                    definition(
                        "adam.get_weather",
                        "Get the current demo weather for a city",
                        {"city": {"type": "string"}},
                        ["city"],
                    ),
                    definition(
                        "adam.celsius_to_fahrenheit",
                        "Convert Celsius to Fahrenheit",
                        {"celsius": {"type": "number"}},
                        ["celsius"],
                    ),
                ],
            }
        )
        anas_bundle = await sdk.tools.create_tool_bundle(
            body={
                "name": "anas-builder-tools",
                "description": "Private working-note utilities available only to Anas",
                "transport": "callback",
                "callback": {"url": f"http://127.0.0.1:{tool_port}/anas"},
                "tools": [
                    definition(
                        "anas.save_note",
                        "Save a private engineering note",
                        {"text": {"type": "string"}},
                        ["text"],
                    ),
                    definition("anas.list_notes", "List private engineering notes", {}, []),
                ],
            }
        )

        adam_binding = await sdk.tools.create_tool_binding(
            body={
                "bundleId": adam_bundle["id"],
                "scope": {
                    "level": "profile",
                    "instanceId": instance_id,
                    "profileId": adam_profile_id,
                },
                "approvalPolicy": "never",
            }
        )
        anas_binding = await sdk.tools.create_tool_binding(
            body={
                "bundleId": anas_bundle["id"],
                "scope": {
                    "level": "profile",
                    "instanceId": instance_id,
                    "profileId": anas["id"],
                },
                "approvalPolicy": "never",
            }
        )

        adam_session = await sdk.runtime.create_session(
            instance_id=instance_id,
            profile_id=adam_profile_id,
            body={"title": "Adam demo", "toolBindingIds": [adam_binding["id"]]},
        )
        anas_session = await sdk.runtime.create_session(
            instance_id=instance_id,
            profile_id=anas["id"],
            body={"title": "Anas demo", "toolBindingIds": [anas_binding["id"]]},
        )

        weather = await sdk.tools.execute_tool_call(
            body={
                "callId": str(uuid.uuid4()),
                "tool": "adam.get_weather",
                "arguments": {"city": "Casablanca"},
                "target": {
                    "level": "profile",
                    "instanceId": instance_id,
                    "profileId": adam_profile_id,
                },
            }
        )
        saved = await sdk.tools.execute_tool_call(
            body={
                "callId": str(uuid.uuid4()),
                "tool": "anas.save_note",
                "arguments": {"text": "The two-profile Hermes demo is alive."},
                "target": {
                    "level": "profile",
                    "instanceId": instance_id,
                    "profileId": anas["id"],
                },
            }
        )

        print(
            "\nCreated:\n"
            + json.dumps(
                {
                    "instanceId": instance_id,
                    "profiles": {
                        "Adam": {
                            "profileId": adam_profile_id,
                            "sessionId": adam_session["id"],
                            "toolBindingId": adam_binding["id"],
                            "tools": ["adam.get_weather", "adam.celsius_to_fahrenheit"],
                        },
                        "Anas": {
                            "profileId": anas["id"],
                            "sessionId": anas_session["id"],
                            "toolBindingId": anas_binding["id"],
                            "tools": ["anas.save_note", "anas.list_notes"],
                        },
                    },
                    "toolResults": {"Adam": weather, "Anas": saved},
                },
                indent=2,
            )
        )
        await asyncio.to_thread(input, "\nPress Enter to delete the demo container and exit... ")
    finally:
        if sdk is not None and instance_id is not None:
            try:
                await sdk.control_plane.delete_instance(instance_id=instance_id, retain_data=False)
            except Exception as exc:
                print(f"Cleanup warning: {exc}")
        if sdk is not None:
            await sdk.aclose()
        if control_server is not None:
            control_server.should_exit = True
        if control_task is not None:
            await control_task
        tool_server.should_exit = True
        await tool_task


if __name__ == "__main__":
    asyncio.run(main())
