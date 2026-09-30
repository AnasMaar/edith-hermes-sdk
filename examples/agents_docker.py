"""Agno-style ergonomics, real Hermes Docker runtime. Add --run for local Ollama inference."""

import asyncio
import sys

from edith_hermes import Agent, Docker, Hermes, Model, tool


@tool
def celsius_to_fahrenheit(celsius: float) -> dict[str, float]:
    """Convert a temperature from Celsius to Fahrenheit."""
    return {"fahrenheit": celsius * 1.8 + 32}


notes: list[str] = []


@tool
def save_note(text: str) -> dict[str, int]:
    """Save an engineering note for Anas."""
    notes.append(text)
    return {"note_count": len(notes)}


async def main() -> None:
    model = Model(
        "gemma3-tools:12b",
        provider="custom",
        base_url="http://host.docker.internal:11434/v1",
        api_key="ollama",
    )
    async with Hermes.local(runtime=Docker()) as hermes:
        instance = await hermes.create_instance(
            "two-agents",
            agents=[
                Agent(
                    "Adam",
                    instructions="You are Adam's assistant. Use the temperature tool when asked to convert temperatures.",
                    model=model,
                    tools=[celsius_to_fahrenheit],
                ),
                Agent(
                    "Anas",
                    instructions="You are Anas's engineering assistant.",
                    model=model,
                    tools=[save_note],
                ),
            ],
        )
        for name in ("Adam", "Anas"):
            agent = instance.agent(name)
            session_id = await agent.new_session(title=name + " typed API demo")
            servers = await agent.rpc("mcp.servers.list")
            print(f"{name}: profile={agent.profile_id}, session={session_id}")
            print(servers)
        if "--restart" in sys.argv:
            await instance.restart()
            reopened = await hermes.open_instance(instance.id)
            assert set(reopened.agents) == {"Adam", "Anas"}
            for name in ("Adam", "Anas"):
                await reopened.agent(name).new_session()
                native = await reopened.agent(name).rpc("mcp.servers.list")
                assert len(native["result"]["servers"]) == 1
            print("Restart: both profiles and their tool configurations survived.")
        if "--run" in sys.argv:
            result = await instance.agent("Adam").run(
                "Use celsius_to_fahrenheit to convert 24 Celsius. Reply with the tool's result.",
                timeout=180,
            )
            print(f"Adam [{result.status}]: {result.text}")
            if result.status != "completed":
                raise RuntimeError(str(result.raw))
    print("Demo containers cleaned up.")


if __name__ == "__main__":
    asyncio.run(main())
