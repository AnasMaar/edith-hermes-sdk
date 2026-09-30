"""Typed, composable convenience layer over the complete low-level SDK."""

from __future__ import annotations

import asyncio
import inspect
import json
import secrets
import socket
from collections.abc import AsyncIterator, Callable, Sequence
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Literal, Protocol, cast, get_type_hints

from pydantic import BaseModel, ConfigDict, TypeAdapter, create_model

from .client import AsyncEdithHermes
from .generated.resources import (
    BindingResource,
    InstanceResource,
    ProfileResource,
    RootResource,
    SessionResource,
    TurnResource,
)
from .generated.types_control_plane import InstanceOperation
from .generated.types_runtime import ContentPart
from .generated.types_tools import ToolDefinition
from .resources import UNSET, Unset


class Runtime(Protocol):
    """Implement this protocol to supply another runtime configuration."""

    def to_dict(self) -> dict[str, Any]: ...


@dataclass(frozen=True)
class Docker:
    image: str = "nousresearch/hermes-agent:latest"
    cpu: str = "1"
    memory: str = "2Gi"
    environment: dict[str, str] = field(default_factory=dict, repr=False)
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "container",
            "image": self.image,
            "resources": {"cpu": self.cpu, "memory": self.memory},
            "environment": {k: {"value": v} for k, v in self.environment.items()},
            **self.options,
        }


@dataclass(frozen=True)
class Kubernetes:
    image: str
    namespace: str = "hermes-runtimes"
    cpu: str = "1"
    memory: str = "2Gi"
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "kubernetes",
            "image": self.image,
            "kubernetes": {"namespace": self.namespace},
            "resources": {"cpu": self.cpu, "memory": self.memory},
            **self.options,
        }


@dataclass(frozen=True)
class Process:
    executable: str = "hermes"
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "process", "executable": self.executable, **self.options}


@dataclass(frozen=True)
class External:
    endpoint: str
    authorization: dict[str, str] = field(default_factory=lambda: {"scheme": "none"}, repr=False)
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "external",
            "endpoint": self.endpoint,
            "authorization": self.authorization,
            **self.options,
        }


@dataclass(frozen=True)
class Tool:
    function: Callable[..., Any] = field(repr=False)
    name: str
    description: str
    arguments: type[BaseModel] = field(repr=False)

    @classmethod
    def from_function(cls, function: Callable[..., Any]) -> Tool:
        hints = get_type_hints(function)
        fields: dict[str, Any] = {}
        for name, parameter in inspect.signature(function).parameters.items():
            if parameter.kind in {
                parameter.VAR_POSITIONAL,
                parameter.VAR_KEYWORD,
                parameter.POSITIONAL_ONLY,
            }:
                raise TypeError(
                    "Tools require named, annotated parameters; *args/**kwargs are unsupported"
                )
            if name not in hints:
                raise TypeError(f"Tool parameter {name!r} needs a type annotation")
            fields[name] = (
                hints[name],
                ... if parameter.default is parameter.empty else parameter.default,
            )
        model = create_model(
            function.__name__ + "Arguments", __config__=ConfigDict(extra="forbid"), **fields
        )
        return cls(
            function, function.__name__, inspect.getdoc(function) or function.__name__, model
        )

    def definition(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.arguments.model_json_schema(),
        }

    async def invoke(self, arguments: dict[str, Any]) -> Any:
        parsed = self.arguments.model_validate(arguments)
        values = {name: getattr(parsed, name) for name in type(parsed).model_fields}
        if inspect.iscoroutinefunction(self.function):
            result = await self.function(**values)
        else:
            result = await asyncio.to_thread(self.function, **values)
        return TypeAdapter(Any).dump_python(result, mode="json")


def tool(function: Callable[..., Any]) -> Tool:
    """Expose an annotated Python function to Hermes; generates its JSON schema."""
    return Tool.from_function(function)


@dataclass(frozen=True)
class Model:
    id: str
    provider: str
    base_url: str | None = None
    api_key: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class Agent:
    """Declarative profile configuration; does no I/O until attached to an instance."""

    name: str
    instructions: str = ""
    model: str | Model | None = None
    provider: str | None = None
    tools: Sequence[Tool | Callable[..., Any]] = ()
    profile_options: dict[str, Any] = field(default_factory=dict)
    session_options: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict, kw_only=True)
    max_turns: int | None = field(default=None, kw_only=True)
    toolsets: Sequence[str] | None = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Agent name must not be empty")
        if self.max_turns is not None and (
            not isinstance(self.max_turns, int)
            or isinstance(self.max_turns, bool)
            or self.max_turns < 1
        ):
            raise ValueError("max_turns must be a positive integer")
        # Validate Python tool definitions before provisioning a runtime.
        object.__setattr__(
            self, "tools", tuple(t if isinstance(t, Tool) else tool(t) for t in self.tools)
        )
        if len({t.name for t in cast(Sequence[Tool], self.tools)}) != len(self.tools):
            raise ValueError("Tool names must be unique within an agent")

    def profile(self) -> dict[str, Any]:
        model = self.model
        result = {
            "name": self.name,
            "soul": self.instructions,
            **({"model": model.id if isinstance(model, Model) else model} if model else {}),
            **(
                {"provider": model.provider}
                if isinstance(model, Model)
                else {"provider": self.provider}
                if self.provider
                else {}
            ),
            **self.profile_options,
        }
        config = {**dict(result.get("config") or {}), **self.config}
        if self.max_turns is not None:
            config["agent.max_turns"] = self.max_turns
        if self.toolsets is not None:
            config["platform_toolsets.cli"] = list(self.toolsets)
        if isinstance(model, Model):
            if model.base_url and model.provider == "custom":
                # Hermes validates named custom providers; the bare placeholder
                # cannot reliably select a configured custom endpoint.
                result["provider"] = "custom:edith"
                config["providers.edith"] = {
                    "name": "edith",
                    "base_url": model.base_url,
                    "api_key": model.api_key or "no-key-required",
                    "models": [model.id],
                }
            elif model.base_url:
                config["model.base_url"] = model.base_url
            if model.api_key and model.provider != "custom":
                config["model.api_key"] = model.api_key
        if config:
            result["config"] = config
        return result


@dataclass(frozen=True)
class RunResult:
    text: str
    status: str
    session_id: str
    turn_id: str
    raw: dict[str, Any] = field(repr=False)


class BoundAgent(ProfileResource):
    def __init__(self, instance: Instance, config: Agent, profile_id: str):
        super().__init__(instance.hermes.sdk, instance_id=instance.id, profile_id=profile_id)
        self.instance, self.config, self.profile_id = instance, config, profile_id
        self.session_id: str | None = None
        self._lock = asyncio.Lock()
        self._owned_tools: dict[str, tuple[str, str]] = {}

    @property
    def session(self) -> SessionResource:
        """The active session, including turns, actions and the event stream."""
        if self.session_id is None:
            raise RuntimeError("Create a session with new_session() or run() first")
        return self.sessions(self.session_id)

    async def rpc(self, method: str, **params: Any) -> Any:
        """Escape hatch to any native Hermes gateway method."""
        return await self.instance.hermes.sdk.gateway.invoke(
            method, instance_id=self.instance.id, profile_id=self.profile_id, params=params
        )

    async def new_session(self, *, title: str | None = None) -> str:
        async with self._lock:
            return await self._new_session(title=title)

    async def _new_session(self, *, title: str | None = None) -> str:
        body = {**self.config.session_options}
        if title:
            body["title"] = title
        # The model is already configured on the profile. Session overrides can
        # discard provider endpoint/credential configuration in native Hermes.
        result = await self.instance.hermes.sdk.runtime.create_session(
            instance_id=self.instance.id, profile_id=self.profile_id, body=body
        )
        self.session_id = str(result["id"])
        return self.session_id

    async def open_session(self, session_id: str) -> SessionResource:
        """Select an existing conversation after checking its instance/profile ownership."""
        async with self._lock:
            selected = self.sessions(session_id)
            await selected.get()
            self.session_id = session_id
            return selected

    async def add_tools(self, tools: Sequence[Tool | Callable[..., Any]]) -> BindingResource:
        """Attach another Python tool bundle to this profile and refresh its live sessions."""
        async with self._lock:
            return await self._add_tools(tools)

    async def _add_tools(self, tools: Sequence[Tool | Callable[..., Any]]) -> BindingResource:
        host = self.instance.hermes._host
        if host is None:
            raise RuntimeError("Python tools require Hermes.local() or a reachable ToolHost")
        normalized = [t if isinstance(t, Tool) else tool(t) for t in tools]
        if not normalized:
            raise ValueError("At least one tool is required")
        callback = host.register(normalized)
        bundle_id = None
        try:
            bundle = await self.instance.hermes.tools.bundles.create(
                name=self.config.name + "-tools",
                transport="callback",
                callback={"url": callback},
                tools=cast(list[ToolDefinition], [t.definition() for t in normalized]),
            )
            bundle_id = bundle["id"]
            binding = await self.instance.hermes.tools.bindings.create(
                bundle_id=bundle_id,
                scope={
                    "level": "profile",
                    "instanceId": self.instance.id,
                    "profileId": self.profile_id,
                },
            )
        except BaseException:
            host.unregister(callback)
            if bundle_id is not None:
                # Preserve the original provisioning/transport failure even if the
                # best-effort catalog cleanup also fails.
                with suppress(Exception):
                    await self.instance.hermes.tools.bundles(bundle_id).delete()
            raise
        self._owned_tools[binding["id"]] = (callback, bundle_id)
        return self.instance.hermes.tools.bindings(binding["id"])

    async def remove_tools(self, binding_id: str) -> None:
        """Remove this profile's binding; revoke owned callbacks when no binding still uses them."""
        async with self._lock:
            await self._remove_tools(binding_id)

    async def _remove_tools(self, binding_id: str) -> None:
        binding = self.instance.hermes.tools.bindings(binding_id)
        value = await binding.get()
        if (
            value["scope"].get("instanceId") != self.instance.id
            or value["scope"].get("profileId") != self.profile_id
        ):
            raise ValueError("Tool binding does not belong to this agent")
        await binding.delete()
        await self._release_tools(binding_id)

    async def _release_tools(self, binding_id: str) -> None:
        owned = self._owned_tools.get(binding_id)
        if owned is None:
            return
        callback, bundle_id = owned
        existing = await self.instance.hermes.tools.bindings.list()
        if any(binding["bundleId"] == bundle_id for binding in existing["items"]):
            return
        host = self.instance.hermes._host
        if host:
            host.unregister(callback)
        self._owned_tools.pop(binding_id)
        from .errors import NotFoundError

        with suppress(NotFoundError):
            await self.instance.hermes.tools.bundles(bundle_id).delete()

    async def _start(self, prompt: str | list[ContentPart], **options: Any) -> TurnResource:
        if self.session_id is None:
            await self._new_session()
        turn = await self.session.turns.submit(content=prompt, **options)
        return self.session.turns(turn["id"])

    async def start(
        self,
        prompt: str | list[ContentPart],
        *,
        mode: Literal["enqueue", "steer"] | Unset = UNSET,
        tool_binding_ids: list[str] | Unset = UNSET,
        metadata: dict[str, Any] | Unset = UNSET,
        idempotency_key: str | Unset = UNSET,
    ) -> TurnResource:
        """Submit without waiting; the handle supports get/wait/stop/steer/approve.

        Consume agent.session.events() separately for the session's SSE stream.
        Tool bindings must already exist; support is determined by the server.
        """
        async with self._lock:
            return await self._start(
                prompt,
                mode=mode,
                tool_binding_ids=tool_binding_ids,
                metadata=metadata,
                idempotency_key=idempotency_key,
            )

    async def run(
        self,
        prompt: str | list[ContentPart],
        *,
        timeout: float = 300,
        tool_binding_ids: list[str] | Unset = UNSET,
        metadata: dict[str, Any] | Unset = UNSET,
        idempotency_key: str | Unset = UNSET,
    ) -> RunResult:
        """Wait for completion or a pending approval, not just the submit ACK."""
        if timeout < 0:
            raise ValueError("timeout must be nonnegative")
        async with self._lock:
            handle = await self._start(
                prompt,
                tool_binding_ids=tool_binding_ids,
                metadata=metadata,
                idempotency_key=idempotency_key,
            )
            turn = cast(dict[str, Any], await handle.wait(timeout=timeout))
            text = "\n".join(
                part.get("text", "")
                for part in turn.get("output", [])
                if part.get("type") == "text"
            )
            assert self.session_id
            return RunResult(text, turn["status"], self.session_id, turn["id"], turn)


class Instance(InstanceResource):
    def __init__(self, hermes: Hermes, instance_id: str):
        super().__init__(hermes.sdk, instance_id=instance_id)
        self.hermes, self.id = hermes, instance_id
        self.agents: dict[str, BoundAgent] = {}

    def agent(self, name: str) -> BoundAgent:
        return self.agents[name]

    async def add_agent(self, config: Agent, *, profile_id: str | None = None) -> BoundAgent:
        if config.name in self.agents:
            raise ValueError(f"Agent {config.name!r} is already attached")
        if config.tools and self.hermes._host is None:
            raise RuntimeError("Python tools require Hermes.local() or a reachable ToolHost")
        if profile_id is None:
            profile = await self.hermes.sdk.control_plane.create_profile(
                instance_id=self.id, body=config.profile()
            )
            profile_id = str(profile["id"])
        bound = BoundAgent(self, config, profile_id)
        if config.tools:
            await bound.add_tools(config.tools)
        self.agents[config.name] = bound
        return bound

    async def delete(self, *, retain_data: bool | Unset = UNSET) -> InstanceOperation:
        result = await super().delete(retain_data=retain_data)
        for agent in self.agents.values():
            for binding_id in list(agent._owned_tools):
                await agent._release_tools(binding_id)
        self.hermes._created.pop(self.id, None)
        return result

    async def restart(self) -> None:
        await self.hermes.sdk.control_plane.change_instance_state(
            instance_id=self.id, action="restart"
        )
        for agent in self.agents.values():
            agent.session_id = None


class ToolHost:
    """Expose only capability-authenticated callbacks/MCP, not anonymous control-plane routes."""

    def __init__(self, base_url: str):
        from urllib.parse import urlsplit

        parsed = urlsplit(base_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.query
            or parsed.fragment
            or parsed.username
        ):
            raise ValueError(
                "ToolHost needs a reachable http(s) base URL without credentials/query/fragment"
            )
        from fastapi import FastAPI, HTTPException, Request

        self.base_url = base_url.rstrip("/")
        self.tools: dict[str, dict[str, Tool]] = {}
        self.app = FastAPI()

        async def callback(key: str, request: Request) -> dict[str, Any]:
            functions = self.tools.get(key)
            if functions is None:
                raise HTTPException(404)
            call = await request.json()
            if call["tool"] not in functions:
                raise HTTPException(404)
            try:
                value = await functions[call["tool"]].invoke(call.get("arguments") or {})
                return {
                    "callId": call["callId"],
                    "isError": False,
                    "content": [{"type": "text", "text": json.dumps(value)}],
                    "structuredContent": value if isinstance(value, dict) else {"result": value},
                }
            except Exception as exc:
                return {
                    "callId": call["callId"],
                    "isError": True,
                    "content": [{"type": "text", "text": str(exc)}],
                }

        callback.__annotations__["request"] = Request
        self.app.post("/callbacks/{key}")(callback)

    def register(self, tools: Sequence[Tool]) -> str:
        if len({t.name for t in tools}) != len(tools):
            raise ValueError("Tool names must be unique within an agent")
        key = secrets.token_urlsafe(32)
        self.tools[key] = {t.name: t for t in tools}
        return f"{self.base_url}/callbacks/{key}"

    def unregister(self, callback_url: str) -> None:
        """Revoke a callback capability, e.g. after removing its tool binding."""
        prefix = self.base_url + "/callbacks/"
        if not callback_url.startswith(prefix):
            raise ValueError("Callback belongs to a different tool host")
        self.tools.pop(callback_url[len(prefix) :], None)


class _ToolHost(ToolHost):
    def __init__(self, listener: socket.socket):
        from fastapi import Request
        from fastapi.responses import Response

        self.port = listener.getsockname()[1]
        super().__init__(f"http://127.0.0.1:{self.port}")
        self.sdk: AsyncEdithHermes | None = None

        async def mcp(binding_id: str, request: Request) -> Response:
            assert self.sdk and self.sdk._local_http
            response = await self.sdk._local_http.post(
                "/internal/mcp/" + binding_id,
                content=await request.body(),
                headers={
                    "Authorization": request.headers.get("authorization", ""),
                    "Content-Type": "application/json",
                },
            )
            return Response(
                response.content, status_code=response.status_code, media_type="application/json"
            )

        # Resolve local FastAPI imports despite postponed annotations.
        mcp.__annotations__["request"] = Request
        mcp.__annotations__["return"] = Response
        self.app.post("/internal/mcp/{binding_id}")(mcp)


class Hermes(RootResource):
    """High-level orchestration; .sdk preserves every existing low-level namespace."""

    def __init__(
        self,
        sdk: AsyncEdithHermes,
        *,
        runtime: Runtime | None = None,
        owner: dict[str, str] | None = None,
        tool_host: ToolHost | None = None,
    ):
        super().__init__(sdk)
        self.sdk, self.runtime = sdk, runtime
        self.owner = owner or {"tenantId": "local", "subjectId": "local-user"}
        self._host = tool_host
        self._created: dict[str, Instance] = {}

    @classmethod
    def remote(
        cls,
        base_url: str,
        *,
        token: str | None = None,
        runtime: Runtime | None = None,
        owner: dict[str, str] | None = None,
        tool_host: ToolHost | None = None,
        timeout: float = 30,
        max_retries: int = 2,
    ) -> Hermes:
        """Connect to a control plane. No runtime/auth/storage service is implicitly installed."""
        return cls(
            AsyncEdithHermes.remote(
                base_url=base_url, token=token, timeout=timeout, max_retries=max_retries
            ),
            runtime=runtime,
            owner=owner,
            tool_host=tool_host,
        )

    async def __aenter__(self) -> Hermes:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close client connections; does not delete remote instances or stop an external ToolHost."""
        await self.sdk.aclose()

    @property
    def cloud(self) -> Any:
        """Unpinned provider extension API; no official typed cloud contract is available."""
        return self.sdk.cloud

    @classmethod
    @asynccontextmanager
    async def local(
        cls,
        *,
        runtime: Runtime | None = None,
        state: str = ".edith-hermes/state.db",
        cleanup: bool = True,
        tools_host: str | None = None,
        settings: Any = None,
    ) -> AsyncIterator[Hermes]:
        """Local Docker/process control plane; optional SQLite state, no PostgreSQL/OIDC/KMS.

        cleanup=True deletes instances created in this context. Set False for persistent
        instances; their Python callback tools are only reachable while this context lives.
        Kubernetes control planes should run in-cluster (use Hermes(existing_sdk,...)).
        """
        import uvicorn
        from edith_hermes_control_plane.config import Settings

        effective_runtime = runtime or Docker()
        listener = socket.socket()
        listener.bind(("0.0.0.0", 0))
        listener.listen(128)
        listener.setblocking(False)
        host = _ToolHost(listener)
        path = Path(state).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        effective = settings or Settings(
            database_url=f"sqlite+aiosqlite:///{path}",
            enabled_runtime_providers=[effective_runtime.to_dict()["kind"]],
            worker_poll_seconds=0.1,
        )
        advertised_host = tools_host or (
            "host.docker.internal"
            if effective_runtime.to_dict()["kind"] == "container"
            else "127.0.0.1"
        )
        effective = replace(effective, public_base_url=f"http://{advertised_host}:{host.port}")
        try:
            sdk = await AsyncEdithHermes.local(settings=effective)
        except BaseException:
            listener.close()
            raise
        host.sdk = sdk
        result = cls(
            sdk,
            runtime=effective_runtime,
            owner={
                "tenantId": effective.anonymous_tenant_id,
                "subjectId": effective.anonymous_subject_id,
            },
        )
        result._host = host
        server = uvicorn.Server(uvicorn.Config(host.app, log_level="error", access_log=False))
        task = asyncio.create_task(server.serve(sockets=[listener]))
        try:
            while not server.started:
                if task.done():
                    await task
                    raise RuntimeError("Tool host stopped before starting")
                await asyncio.sleep(0.01)
            yield result
        finally:
            cleanup_errors: list[Exception] = []
            try:
                if cleanup:
                    for instance in list(result._created.values()):
                        try:
                            await instance.delete()
                        except Exception as exc:
                            # A failed provider must not skip the other owned runtimes.
                            # Surface the failure after attempting every owned cleanup.
                            cleanup_errors.append(exc)
            finally:
                server.should_exit = True
                try:
                    await task
                finally:
                    listener.close()
                    await sdk.aclose()
            if cleanup_errors:
                raise cleanup_errors[0]

    async def open_instance(self, instance_id: str) -> Instance:
        """Attach handles to an existing SDK-managed instance; never takes cleanup ownership."""
        await self.sdk.control_plane.get_instance(instance_id=instance_id)
        profiles = await self.sdk.control_plane.list_profiles(instance_id=instance_id)
        instance = Instance(self, instance_id)
        for profile in profiles["items"]:
            config = Agent(profile["name"])
            instance.agents[config.name] = BoundAgent(instance, config, profile["id"])
        return instance

    async def create_instance(
        self,
        name: str,
        *,
        agents: Sequence[Agent] = (),
        timeout: float = 300,
        runtime: Runtime | None = None,
        owner: dict[str, str] | None = None,
        options: dict[str, Any] | None = None,
    ) -> Instance:
        if timeout < 0:
            raise ValueError("timeout must be nonnegative")
        selected_runtime = runtime or self.runtime
        if selected_runtime is None:
            raise ValueError("Select a runtime on Hermes or create_instance(runtime=...)")
        configs = list(agents) or [Agent("main")]
        if len({a.name for a in configs}) != len(configs):
            raise ValueError("Agent names must be unique within an instance")
        if any(a.tools for a in configs) and self._host is None:
            raise RuntimeError("Python tools require Hermes.local() or a reachable ToolHost")
        if options and {"owner", "name", "runtime", "bootstrap"} & options.keys():
            raise ValueError("options cannot override owner, name, runtime or bootstrap")
        job = await self.sdk.control_plane.provision_user_instance(
            body={
                **(options or {}),
                "owner": owner or self.owner,
                "name": name,
                "runtime": selected_runtime.to_dict(),
                "bootstrap": {"profile": configs[0].profile()},
            }
        )
        ready = await self.sdk.wait_for_provisioning_job(
            job["id"], timeout=timeout, poll_interval=0.25
        )
        if ready["phase"] != "ready":
            raise RuntimeError(f"Provisioning failed: {ready.get('error')}")
        instance = Instance(self, ready["instanceId"])
        self._created[instance.id] = instance
        try:
            await instance.add_agent(configs[0], profile_id=ready["profileId"])
            for config in configs[1:]:
                await instance.add_agent(config)
        except BaseException:
            # This helper owns only the newly provisioned runtime. Never leave
            # it running after a failed tool/secondary-profile attachment.
            with suppress(Exception):
                await instance.delete()
            raise
        return instance
