"""Opt-in real Docker/Hermes checks. Creates/deletes only its own instance.

Run with --model <installed-model> for a real local Ollama turn. Configure
the model at the Ollama server with at least 64K context; an OpenAI-compatible
request/profile override alone does not change Ollama's serving context.
No cloud provider or API key is selected by this script.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import tempfile
from pathlib import Path

from edith_hermes import Agent, Docker, Hermes, Model, tool
from edith_hermes.errors import RemoteError


async def main(model: str | None, direct_tools: bool = False) -> None:
    failures = []
    tool_calls = []

    @tool
    def verification_multiply(a: int, b: int) -> dict[str, int]:
        """Multiply two integers and return their exact product."""
        tool_calls.append((a, b))
        return {"product": a * b}

    async def check(name, work):
        try:
            result = await work()
            print(
                json.dumps({"check": name, "status": "passed", "result": result}, default=str),
                flush=True,
            )
        except Exception as exc:
            failures.append(name)
            print(json.dumps({"check": name, "status": "failed", "error": str(exc)}), flush=True)

    with tempfile.TemporaryDirectory(prefix="edith-live-") as state:
        async with Hermes.local(runtime=Docker(), state=str(Path(state) / "state.db")) as hermes:
            instance = await hermes.create_instance(
                "sdk-live-verification",
                agents=[
                    Agent(
                        "Adam",
                        instructions="You are Adam. Use verification_multiply when asked to multiply. Be concise.",
                        model=Model(
                            model,
                            "custom",
                            base_url="http://host.docker.internal:11434/v1",
                            api_key="ollama",
                        )
                        if model
                        else None,
                        max_turns=8 if model else None,
                        toolsets=[] if direct_tools else None,
                        config={"tool_search.enabled": "off"} if direct_tools else {},
                        tools=[verification_multiply],
                    ),
                    Agent(
                        "Anas",
                        instructions="You are Anas. Be concise.",
                        model=Model(
                            model,
                            "custom",
                            base_url="http://host.docker.internal:11434/v1",
                            api_key="ollama",
                        )
                        if model
                        else None,
                        profile_options={"config": {"model.ollama_num_ctx": 65536}}
                        if model
                        else {},
                    ),
                ],
            )
            print(
                json.dumps(
                    {"check": "provision_two_profiles", "status": "passed", "instance": instance.id}
                ),
                flush=True,
            )
            adam, anas = instance.agent("Adam"), instance.agent("Anas")

            async def mcp():
                servers = await adam.native.mcp.servers.list()
                assert len(servers["servers"]) == 1
                probe = await adam.native.mcp.servers.test(name=servers["servers"][0]["name"])
                assert probe["ok"], probe
                assert [t["name"] for t in probe["tools"]] == ["verification_multiply"], probe
                assert not (await anas.native.mcp.servers.list())["servers"]
                return {"tools": [t["name"] for t in probe["tools"]]}

            await check("native_mcp_discovery_and_profile_separation", mcp)

            async def profile_config():
                await anas.update(
                    soul="You are Anas, the verification assistant.", config={"agent.max_turns": 7}
                )
                result = await anas.native.config.get(key="full")
                assert result.get("config", {}).get("agent", {}).get("max_turns") == 7
                return {"max_turns": 7}

            await check("profile_update_readback", profile_config)

            async def sessions():
                session = await anas.sessions.create(
                    title="verification",
                    working_directory="/tmp",
                    extra_body={
                        "messages": [
                            {"role": "user", "content": "This is verification history."},
                            {"role": "assistant", "content": "Acknowledged."},
                        ]
                    },
                )
                handle = anas.sessions(session["id"])
                activated = await handle.action(body={"type": "activate"})
                assert activated["id"] == session["id"]
                branch = await handle.action(body={"type": "branch"})
                assert branch["id"] != session["id"]
                await anas.sessions(branch["id"]).action(body={"type": "close"})
                await anas.sessions(branch["id"]).delete()
                await handle.action(body={"type": "close"})
                resumed = await handle.action(body={"type": "resume"})
                assert resumed["nativeSessionId"]
                await handle.action(body={"type": "close"})
                await handle.delete()
                return {"resumed": True, "branched": True, "deleted": True}

            await check("session_create_branch_close_resume_delete", sessions)

            async def duplex():
                async with adam.connect() as connection:
                    response = await connection.call("ping")
                    assert response is not None
                    return {"persistent_rpc": True}

            await check("persistent_native_connection", duplex)

            async def delete_profile():
                profile = await instance.profiles.create(
                    name="DisposableVerification", clone_from="Anas"
                )
                handle = instance.profiles(profile["id"])
                await handle.delete()
                try:
                    await handle.get()
                except RemoteError as exc:
                    assert exc.status == 404
                else:
                    raise AssertionError("Registry still contains deleted profile")
                native = await adam.native.profiles.list()
                assert "DisposableVerification".lower() not in json.dumps(native).lower(), native
                return {"native_and_registry_removed": True}

            await check("profile_clone_and_native_delete", delete_profile)

            if model:

                async def model_turn():
                    await adam.new_session(title="Model/tool verification")
                    result = await adam.run(
                        "Call verification_multiply with a=12 and b=8. Then report the product.",
                        timeout=300,
                    )
                    status = await adam.native.mcp.servers.status()
                    print(
                        json.dumps({"check": "native_mcp_status_after_turn", "result": status}),
                        flush=True,
                    )
                    assert result.status == "completed", result.raw
                    assert (12, 8) in tool_calls, {
                        "text": result.text,
                        "observed_calls": tool_calls,
                        "mcp_status": status,
                    }
                    assert "96" in result.text, result.text
                    return {"text": result.text, "tool_calls": tool_calls}

                await check("real_local_model_tool_turn", model_turn)

                async def dynamic_tools():
                    calls = []

                    def verification_add(a: int, b: int) -> dict[str, int]:
                        """Add two integers and return their exact sum."""
                        calls.append((a, b))
                        return {"sum": a + b}

                    binding = await adam.add_tools([verification_add])
                    value = await binding.get()
                    assert len((await adam.native.mcp.servers.list())["servers"]) == 2
                    assert not (await anas.native.mcp.servers.list())["servers"]
                    selected = await adam.open_session(adam.session_id)
                    assert (await selected.get())["profileId"] == adam.profile_id
                    result = await adam.run(
                        "A new profile tool was just registered: verification_add. Use tool_search to discover it if it is deferred, then invoke the exact returned tool name with a=19 and b=23. Report the sum from its output; do not calculate it yourself.",
                        timeout=300,
                    )
                    assert result.status == "completed", result.raw
                    assert (19, 23) in calls, {
                        "text": result.text,
                        "observed_calls": calls,
                        "tool_steps": [
                            {"name": item.get("name"), "args": item.get("args")}
                            for item in (
                                await adam.native.session.history(session_id=adam.session_id)
                            ).get("messages", [])
                            if item.get("role") == "tool"
                        ],
                    }
                    assert "42" in result.text
                    await adam.remove_tools(value["id"])
                    assert len((await adam.native.mcp.servers.list())["servers"]) == 1
                    return {
                        "text": result.text,
                        "added_to_existing_session": True,
                        "removed": True,
                        "other_profile_unchanged": True,
                    }

                await check("dynamic_tool_add_call_remove", dynamic_tools)

            async def remove_binding():
                bindings = await hermes.tools.bindings.list(
                    instance_id=instance.id, profile_id=adam.profile_id
                )
                for binding in bindings["items"]:
                    await adam.remove_tools(binding["id"])
                assert not (await adam.native.mcp.servers.list())["servers"]
                assert not hermes._host.tools
                return {"native_mcp_removed": True}

            await check("binding_removal_reconciles_native", remove_binding)
        print(json.dumps({"check": "owned_instance_cleanup", "status": "passed"}), flush=True)
    if failures:
        raise SystemExit("Failed checks: " + ", ".join(failures))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None)
    parser.add_argument(
        "--direct-tools",
        action="store_true",
        help="Expose MCP schemas directly instead of native progressive tool search",
    )
    args = parser.parse_args()
    asyncio.run(main(args.model, args.direct_tools))
