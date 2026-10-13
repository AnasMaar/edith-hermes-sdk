"""Explicit bindings for product-owned versioned extensions, separate from native RPC."""
from __future__ import annotations

from typing import Any, Literal, Protocol, TypedDict, cast


class ExtensionTransport(Protocol):
    async def call(self, method: str, *, timeout: float = 30, **params: Any) -> Any: ...


class PreparedBlueprint(TypedDict):
    profile: str
    name: str
    prompt: str
    schedule: str
    deliver: str
    skills: list[str]


class McpPatch(TypedDict, total=False):
    command: str
    args: list[str]
    url: str
    auth: str | None
    enabled: bool
    env: dict[str, str]
    headers: dict[str, str]
    clear_environment_keys: list[str]
    clear_header_keys: list[str]


class GitInspection(TypedDict):
    root: str
    commonDir: str
    originUrl: str | None
    head: str | None
    status: dict[str, Any]
    branches: list[dict[str, Any]]


class GitObjectRequest(TypedDict):
    path: str
    objectId: str | None
    preferDisk: bool


class CronTriggerReceipt(TypedDict, total=False):
    requestId: str
    profileId: str
    jobId: str
    status: Literal['running', 'completed', 'rejected', 'uncertain']
    lastRunAt: str | None


class RoomToolFact(TypedDict):
    id: str
    memberId: str
    taskId: str
    generation: int
    threadId: str | None
    createdAt: float
    tool: dict[str, Any]


class SkillInventoryEntry(TypedDict):
    id: str
    canonicalId: str
    name: str
    description: str
    category: str
    enabled: bool
    revision: str
    invocationId: str | None


class ReasoningDefaultResult(TypedDict):
    value: None
    effectiveEffort: str | None


class SkillActionReceipt(TypedDict):
    id: str
    profileId: str
    resourceId: str
    kind: Literal['install', 'uninstall', 'update']
    status: Literal['pending', 'running', 'completed', 'failed', 'uncertain']
    pid: int | None
    name: str
    startedAt: float
    completedAt: float | None
    exitCode: int | None


class SkillDocument(TypedDict):
    content: str
    revision: str
    modifiedAtMs: float
    sizeBytes: int


class AsyncHermesExtensions:
    """Capabilities must be checked on the running product extension deployment."""
    def __init__(self, connection: ExtensionTransport, *, profile: str):
        if not profile or profile != profile.strip() or profile.lower() == "all":
            raise ValueError("An extension requires a concrete profile")
        self.connection, self.profile = connection, profile

    async def capabilities(self) -> dict[str, Any]:
        result = await self.connection.call("edith.desktop.v1.capabilities", profile=self.profile)
        if not isinstance(result, dict) or result.get("version") != 1:
            raise ValueError("Unsupported EDITH desktop extension version")
        return cast(dict[str, Any], result)

    async def skill_inventory(self) -> list[SkillInventoryEntry]:
        """Stable file identity, including disabled skills; separate from invocation IDs."""
        result = await self.connection.call('edith.desktop.v1.skills.inventory', profile=self.profile)
        return cast(list[SkillInventoryEntry], result['skills'])

    async def toggle_skill(self, identity: str, *, revision: str, enabled: bool) -> SkillInventoryEntry:
        """Per-skill CAS, preserving secrets and unrelated native configuration."""
        return cast(SkillInventoryEntry, await self.connection.call('edith.desktop.v1.skills.toggle',
            profile=self.profile, id=identity, revision=revision, enabled=enabled))

    async def reset_reasoning(self, session_id: str) -> ReasoningDefaultResult:
        """Clear a session pin through the native profile resolver; no global write."""
        return cast(ReasoningDefaultResult, await self.connection.call(
            'edith.desktop.v1.execution.reasoning_default', profile=self.profile,
            session_id=session_id))

    async def skill_action(self, kind: Literal['install', 'uninstall', 'update'], resource: str, *, request_id: str) -> SkillActionReceipt:
        """Start one owned native skill action; a running receipt is not success."""
        return cast(SkillActionReceipt, await self.connection.call('edith.desktop.v1.skills.action',
            profile=self.profile, request_id=request_id, kind=kind, resource=resource))

    async def skill_operation(self, request_id: str) -> SkillActionReceipt:
        """Reconcile a durable profile-owned receipt without replaying its mutation."""
        return cast(SkillActionReceipt, await self.connection.call('edith.desktop.v1.skills.operation',
            profile=self.profile, request_id=request_id))

    async def skill_content(self, identity: str) -> SkillDocument:
        """Read the owning native document with a content revision and metadata."""
        return cast(SkillDocument, await self.connection.call('edith.desktop.v1.skills.content',
            profile=self.profile, id=identity))

    async def save_skill(self, identity: str, *, revision: str, content: str) -> SkillDocument:
        """CAS wrapper around Hermes's existing foreground skill editor."""
        return cast(SkillDocument, await self.connection.call('edith.desktop.v1.skills.save',
            profile=self.profile, id=identity, revision=revision, content=content))

    async def mcp_revisions(self) -> dict[str, str]:
        result = await self.connection.call("edith.desktop.v1.mcp.revisions", profile=self.profile)
        return dict(result["revisions"])

    async def update_mcp(self, name: str, *, revision: str, patch: McpPatch, request_id: str) -> dict[str, Any]:
        """One per-server CAS update. Never replace a redacted inventory map."""
        return cast(dict[str, Any], await self.connection.call("edith.desktop.v1.mcp.update", profile=self.profile,
                                          name=name, revision=revision, patch=patch, request_id=request_id))

    async def mcp_operation(self, request_id: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.connection.call("edith.desktop.v1.mcp.operation", profile=self.profile, request_id=request_id))

    async def cron_trigger(self, job_id: str, *, request_id: str) -> CronTriggerReceipt:
        """Dispatch through native cron's claim with a durable receipt. Never retry."""
        return cast(CronTriggerReceipt, await self.connection.call('edith.desktop.v1.cron.trigger', profile=self.profile, job_id=job_id, request_id=request_id))

    async def cron_operation(self, request_id: str) -> CronTriggerReceipt:
        """Read the owning backend receipt after a lost reply or app restart."""
        return cast(CronTriggerReceipt, await self.connection.call('edith.desktop.v1.cron.operation', profile=self.profile, request_id=request_id))

    async def prepare_blueprint(self, blueprint: str, values: dict[str, str]) -> PreparedBlueprint:
        """Validate a native blueprint into a draft without creating or executing a job."""
        result = await self.connection.call('edith.desktop.v1.cron.prepare', profile=self.profile, blueprint=blueprint, values=values)
        if not isinstance(result, dict) or result.get('profile') != self.profile:
            raise ValueError('The blueprint draft belongs to another profile')
        return cast(PreparedBlueprint, result)

    async def group_activity(self, room_id: str) -> list[RoomToolFact]:
        """Read native hosted-member tool facts; independent of room orchestration."""
        result=await self.connection.call('edith.desktop.v1.groups.activity',profile=self.profile,room_id=room_id)
        return cast(list[RoomToolFact],result['tools'])

    async def git_inspect(self, path: str) -> GitInspection | None:
        """Host metadata for native Git review; capability-gated versioned extension."""
        return cast(GitInspection | None, await self.connection.call("edith.desktop.v1.git.inspect", profile=self.profile, path=path))

    async def git_objects(self, path: str, requests: list[GitObjectRequest], *, limit: int = 4194304) -> list[dict[str, Any]]:
        """Bounded, read-only blob or workspace reads for native diff expansion."""
        if not 1 <= limit <= 16777216 or len(requests) > 32:
            raise ValueError("Git object reads exceed the supported bounds")
        return cast(list[dict[str, Any]], await self.connection.call("edith.desktop.v1.git.objects", profile=self.profile, path=path, requests=requests, limit=limit))

    async def git_apply(self, path: str, diff: str, *, target: Literal['staged', 'unstaged', 'staged-and-unstaged'], reverse: bool = False) -> dict[str, Any]:
        """Atomically apply a checked native review patch. No mutation retry."""
        if target not in {'staged', 'unstaged', 'staged-and-unstaged'} or not diff or len(diff.encode()) > 8 * 1024 * 1024:
            raise ValueError('Invalid Git patch')
        return cast(dict[str, Any], await self.connection.call('edith.desktop.v1.git.apply', profile=self.profile, path=path, diff=diff, target=target, reverse=reverse))

    async def git_diff(self, path: str, file: str, *, source: Literal['uncommitted', 'staged', 'unstaged'] = 'uncommitted') -> str:
        """Byte-faithful text patch where native REST normalizes CRLF."""
        result = await self.connection.call('edith.desktop.v1.git.diff', profile=self.profile, path=path, file=file, source=source)
        return cast(str, result['diff'])
