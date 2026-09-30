from __future__ import annotations

from typing import Literal

import pytest
from edith_hermes_control_plane.profiles import create_params
from pydantic import BaseModel, ValidationError

from edith_hermes import Agent, Docker, External, Kubernetes, Model, Process, tool


class Note(BaseModel):
    title: str


@tool
def typed_tool(note: Note, mode: Literal["short", "long"] = "short") -> dict[str, str]:
    """Format a note."""
    return {"text": note.title, "mode": mode}


@pytest.mark.asyncio
async def test_function_tools_preserve_types_and_defaults():
    assert await typed_tool.invoke({"note": {"title": "hello"}}) == {
        "text": "hello",
        "mode": "short",
    }
    with pytest.raises(ValidationError):
        await typed_tool.invoke({"note": {"title": "hello"}, "mode": "invalid"})
    with pytest.raises(ValidationError):
        await typed_tool.invoke({"note": {"title": "hello"}, "unexpected": 1})
    assert typed_tool.definition()["inputSchema"]["required"] == ["note"]


@pytest.mark.asyncio
async def test_async_tool():
    @tool
    async def double(value: int) -> int:
        return 2 * value

    assert await double.invoke({"value": 4}) == 8


def test_untyped_tool_is_rejected():
    with pytest.raises(TypeError, match="annotation"):
        tool(lambda value: value)


def test_agent_accepts_functions_and_direct_config_without_mutating_input():
    def greet(name: str) -> str:
        return "Hello " + name

    original = {"config": {"agent.max_turns": 2, "unrelated": "retained"}}
    config = {"model.temperature": 0.2}
    agent = Agent(
        "Adam",
        tools=[greet, typed_tool],
        profile_options=original,
        config=config,
        max_turns=8,
        toolsets=["terminal", "mcp"],
    )
    assert agent.tools[1] is typed_tool
    assert agent.tools[0].name == "greet"
    assert agent.profile()["config"] == {
        "agent.max_turns": 8,
        "unrelated": "retained",
        "model.temperature": 0.2,
        "platform_toolsets.cli": ["terminal", "mcp"],
    }
    assert original["config"]["agent.max_turns"] == 2
    assert config == {"model.temperature": 0.2}


@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_agent_rejects_invalid_max_turns(value):
    with pytest.raises(ValueError, match="positive integer"):
        Agent("Adam", max_turns=value)


def test_invalid_agent_definitions_fail_before_io():
    with pytest.raises(ValueError, match="empty"):
        Agent(" ")
    with pytest.raises(ValueError, match="unique"):
        Agent("Adam", tools=[typed_tool, typed_tool])
    with pytest.raises(TypeError, match="annotation"):
        Agent("Adam", tools=[lambda value: value])


def test_composable_model_and_runtime():
    model = Model("local", "custom", base_url="http://localhost:11434/v1", api_key="secret")
    assert "secret" not in repr(model)
    profile = Agent("Adam", model=model, tools=[typed_tool]).profile()
    assert profile["model"] == "local"
    assert profile["provider"] == "custom:edith"
    assert profile["config"]["providers.edith"]["base_url"].endswith("/v1")
    assert Docker(memory="512Mi").to_dict()["resources"]["memory"] == "512Mi"
    assert Kubernetes("runtime:tag").to_dict()["kind"] == "kubernetes"
    assert Process().to_dict()["kind"] == "process"
    assert External("ws://localhost/api/ws").to_dict()["kind"] == "external"


def test_public_profile_keys_translate_to_native():
    assert create_params(
        {
            "name": "Adam",
            "cloneFrom": "base",
            "includeSkills": False,
            "mirrorCredentials": False,
            "config": {"agent": {"max_turns": 5}},
        }
    ) == {
        "name": "Adam",
        "clone_from": "base",
        "no_skills": True,
        "mirror_credentials": False,
    }


@pytest.mark.asyncio
async def test_local_tool_host_does_not_expose_control_plane():
    import socket

    import httpx

    from edith_hermes.agent import _ToolHost

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        host = _ToolHost(listener)
        callback_url = host.register([typed_tool])
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=host.app), base_url="http://test"
        ) as client:
            assert (await client.get("/v1/instances")).status_code == 404
            assert (await client.post("/callbacks/wrong", json={})).status_code == 404
            response = await client.post(
                callback_url,
                json={
                    "callId": "one",
                    "tool": "typed_tool",
                    "arguments": {"note": {"title": "hello"}},
                },
            )
            assert response.json()["structuredContent"] == {"text": "hello", "mode": "short"}


async def test_local_settings_are_not_mutated_and_process_callbacks_use_loopback(
    tmp_path, monkeypatch
):
    from unittest.mock import AsyncMock

    from edith_hermes_control_plane.config import Settings

    from edith_hermes import AsyncEdithHermes, Hermes

    sdk = AsyncMock(spec=AsyncEdithHermes)
    sdk._transport = AsyncMock()
    start = AsyncMock(return_value=sdk)
    monkeypatch.setattr(AsyncEdithHermes, "local", start)
    settings = Settings(enabled_runtime_providers=["process"], public_base_url="http://untouched")
    async with Hermes.local(runtime=Process(), state=str(tmp_path / "state.db"), settings=settings):
        effective = start.call_args.kwargs["settings"]
        assert effective.public_base_url.startswith("http://127.0.0.1:")
        assert effective is not settings
    assert settings.public_base_url == "http://untouched"
    sdk.aclose.assert_awaited_once()


async def test_local_cleanup_attempts_all_owned_instances_and_closes_sdk(tmp_path, monkeypatch):
    from unittest.mock import AsyncMock

    from edith_hermes import AsyncEdithHermes, Hermes

    sdk = AsyncMock(spec=AsyncEdithHermes)
    sdk._transport = AsyncMock()
    monkeypatch.setattr(AsyncEdithHermes, "local", AsyncMock(return_value=sdk))
    first, second = AsyncMock(), AsyncMock()
    first.delete.side_effect = RuntimeError("provider unavailable")
    with pytest.raises(RuntimeError, match="provider unavailable"):
        async with Hermes.local(runtime=Process(), state=str(tmp_path / "state.db")) as hermes:
            hermes._created["first"] = first
            hermes._created["second"] = second
    first.delete.assert_awaited_once()
    second.delete.assert_awaited_once()
    sdk.aclose.assert_awaited_once()
