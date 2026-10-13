"""Profile-bound bindings for Hermes Desktop's native HTTP API.

This client connects to ``hermes serve`` directly, not the EDITH control plane.
Mutations are never retried: a lost reply can mean the operation was accepted.
"""
from __future__ import annotations

import builtins
from typing import Any, Literal, TypedDict, cast
from urllib.parse import quote, urlsplit

import httpx
from typing_extensions import Required

from .errors import error_from_response


class CronUpdates(TypedDict, total=False):
    name: str
    prompt: str
    schedule: str
    enabled: bool
    deliver: str
    model: str | None
    provider: str | None
    reasoning_effort: str | None
    continuity: bool
    workdir: str | None


class CronCreate(TypedDict, total=False):
    schedule: Required[str]
    name: str
    prompt: str
    paused: bool
    paused_reason: str | None
    deliver: str
    repeat: int | str | None
    skills: list[str] | None
    model: str | None
    provider: str | None
    base_url: str | None
    script: str | None
    context_from: list[str] | None
    enabled_toolsets: list[str] | None
    workdir: str | None
    no_agent: bool


class CronJob(TypedDict, total=False):
    id: str
    job_id: str
    profile: str
    name: str
    prompt: str
    schedule: dict[str, Any]
    enabled: bool
    last_status: str | None
    next_run_at: str | None


class DesktopCapabilities(TypedDict):
    reachable: bool
    operations: list[str]


def _segment(value: str) -> str:
    if not value or value in {".", ".."}:
        raise ValueError("A resource ID must be nonempty")
    return quote(value, safe="")


class AsyncHermesDesktop:
    def __init__(self, http: httpx.AsyncClient, profile: str, *, token: str | None = None,
                 owns_client: bool = False):
        if not profile or profile != profile.strip() or profile.lower() == "all":
            raise ValueError("Desktop operations require a concrete profile")
        self._http, self.profile = http, profile
        self._token, self._owns_client = token, owns_client
        self.cron = DesktopCron(self)
        self.files = DesktopFiles(self)
        self.git = DesktopGit(self)
        self.skills = DesktopSkills(self)
        self.sessions = DesktopSessions(self)

    @classmethod
    def remote(cls, *, base_url: str, profile: str, token: str | None = None,
               timeout: float = 30, http_client: httpx.AsyncClient | None = None) -> AsyncHermesDesktop:
        url = urlsplit(base_url)
        if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
            raise ValueError("Use an HTTP(S) backend URL without embedded credentials")
        http = http_client or httpx.AsyncClient(base_url=base_url.rstrip("/"), timeout=timeout)
        return cls(http, profile, token=token, owns_client=http_client is None)

    def for_profile(self, profile: str) -> AsyncHermesDesktop:
        return AsyncHermesDesktop(self._http, profile, token=self._token)

    async def _request(self, method: str, path: str, *, body: Any = None,
                       query: dict[str, Any] | None = None, timeout: float = 30) -> Any:
        if not path.startswith("/api/") or "?" in path or "#" in path:
            raise ValueError("Desktop paths must be native /api/ routes")
        if isinstance(body, dict) and body.get("profile") is not None and body["profile"] != self.profile:
            raise ValueError("A request body cannot override the bound profile")
        params = {**(query or {}), "profile": self.profile}
        response = await self._http.request(method, path, params=params, json=body,
            headers={"Authorization": f"Bearer {self._token}"} if self._token else {}, timeout=timeout)
        if response.is_error:
            try:
                payload = response.json()
            except ValueError:
                payload = {"detail": response.reason_phrase}
            raise error_from_response(response.status_code, payload)
        if not response.content:
            return None
        if "json" in response.headers.get("content-type", ""):
            return response.json()
        return response.content

    async def capabilities(self) -> DesktopCapabilities:
        response = await self._http.get("/openapi.json", timeout=10,
            headers={"Authorization": f"Bearer {self._token}"} if self._token else {})
        if response.is_error:
            raise error_from_response(response.status_code, {"detail": "Desktop API discovery failed"})
        schema = response.json()
        paths = schema.get("paths")
        if not isinstance(paths, dict):
            raise ValueError("The backend did not return an OpenAPI contract")
        return {"reachable": True, "operations": sorted(
            f"{method.upper()} {path}" for path, operations in paths.items()
            for method in operations if method.lower() in {"get", "post", "put", "patch", "delete"})}

    async def config(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self._request("GET", "/api/config"))

    async def configure(self, updates: dict[str, Any]) -> Any:
        return await self._request("PUT", "/api/config", body=updates)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncHermesDesktop:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()


class DesktopCron:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def list(self) -> list[CronJob]:
        rows = cast(list[CronJob], await self.client._request("GET", "/api/cron/jobs"))
        for row in rows:
            self._owner(row)
        return rows

    def _owner(self, row: CronJob) -> CronJob:
        if row.get("profile") != self.client.profile:
            raise ValueError("The returned schedule belongs to another profile")
        return row

    async def get(self, job_id: str) -> CronJob:
        return self._owner(cast(CronJob, await self.client._request("GET", f"/api/cron/jobs/{_segment(job_id)}")))

    async def create(self, options: CronCreate) -> CronJob:
        """Create through the native scheduler, including atomic paused creation."""
        return self._owner(cast(CronJob, await self.client._request("POST", "/api/cron/jobs", body=options)))

    async def pause(self, job_id: str) -> CronJob:
        await self.get(job_id)
        return self._owner(cast(CronJob, await self.client._request("POST", f"/api/cron/jobs/{_segment(job_id)}/pause")))

    async def resume(self, job_id: str) -> CronJob:
        await self.get(job_id)
        return self._owner(cast(CronJob, await self.client._request("POST", f"/api/cron/jobs/{_segment(job_id)}/resume")))

    async def remove(self, job_id: str) -> Any:
        await self.get(job_id)
        return await self.client._request("DELETE", f"/api/cron/jobs/{_segment(job_id)}")

    async def update(self, job_id: str, updates: CronUpdates) -> CronJob:
        await self.get(job_id)
        return self._owner(cast(CronJob, await self.client._request("PUT", f"/api/cron/jobs/{_segment(job_id)}", body={"updates": updates})))

    async def trigger(self, job_id: str, *, timeout: float = 86400) -> CronJob:
        await self.get(job_id)
        return self._owner(cast(CronJob, await self.client._request("POST", f"/api/cron/jobs/{_segment(job_id)}/trigger", timeout=timeout)))

    async def runs(self, job_id: str, *, limit: int = 20) -> builtins.list[dict[str, Any]]:
        if not 1 <= limit <= 200:
            raise ValueError("Run history limit must be between 1 and 200")
        await self.get(job_id)
        result = await self.client._request("GET", f"/api/cron/jobs/{_segment(job_id)}/runs", query={"limit": limit})
        return cast(builtins.list[dict[str, Any]], result["runs"])

    async def delivery_targets(self) -> builtins.list[dict[str, Any]]:
        result = await self.client._request("GET", "/api/cron/delivery-targets")
        return cast(builtins.list[dict[str, Any]], result["targets"])

    async def blueprints(self) -> builtins.list[dict[str, Any]]:
        result = await self.client._request("GET", "/api/cron/blueprints")
        return cast(builtins.list[dict[str, Any]], result["blueprints"])

    async def instantiate(self, blueprint: str, values: dict[str, str]) -> CronJob:
        return self._owner(cast(CronJob, await self.client._request("POST", "/api/cron/blueprints/instantiate", body={"blueprint": blueprint, "values": values})))


class DesktopFiles:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def list(self, path: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request("GET", "/api/fs/list", query={"path": path}))

    async def read_text(self, path: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request("GET", "/api/fs/read-text", query={"path": path}))

    async def write_text(self, path: str, content: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request("POST", "/api/fs/write-text", body={"path": path, "content": content}))

    async def data_url(self, path: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request("GET", "/api/fs/read-data-url", query={"path": path}))

    async def default_cwd(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request("GET", "/api/fs/default-cwd"))


class DesktopWorktree(TypedDict):
    path: str
    branch: str | None
    isMain: bool
    detached: bool
    locked: bool


class DesktopWorktreeList(TypedDict):
    worktrees: list[DesktopWorktree]


class DesktopWorktreeOptions(TypedDict, total=False):
    name: str
    branch: str
    base: str
    existingBranch: str


class DesktopGit:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def status(self, path: str) -> dict[str, Any] | None:
        return cast(dict[str, Any] | None, await self.client._request("GET", "/api/git/status", query={"path": path}))

    async def review(self, path: str, scope: Literal["uncommitted", "branch"], *, base: str | None = None) -> dict[str, Any]:
        query: dict[str, Any] = {"path": path, "scope": scope}
        if base is not None:
            query["base"] = base
        return cast(dict[str, Any], await self.client._request("GET", "/api/git/review/list", query=query))

    async def diff(self, path: str, file: str, *, scope: str = "uncommitted", base: str | None = None, staged: bool = False) -> str:
        query: dict[str, Any] = {"path": path, "file": file, "scope": scope, "staged": str(staged).lower()}
        if base is not None:
            query["base"] = base
        result = await self.client._request("GET", "/api/git/review/diff", query=query)
        return cast(str, result["diff"])

    async def file_diff(self, path: str, file: str) -> str:
        """Full file against HEAD, including staged and unstaged changes."""
        result = await self.client._request("GET", "/api/git/file-diff", query={"path": path, "file": file})
        return cast(str, result["diff"])

    async def change(self, action: Literal["stage", "unstage", "revert"], path: str, file: str | None = None) -> Any:
        return await self.client._request("POST", f"/api/git/review/{action}", body={"path": path, "file": file})

    async def commit(self, path: str, message: str, *, push: bool = False) -> Any:
        return await self.client._request("POST", "/api/git/review/commit", body={"path": path, "message": message, "push": push})

    async def push(self, path: str) -> Any:
        return await self.client._request("POST", "/api/git/review/push", body={"path": path})

    async def create_pr(self, path: str) -> Any:
        return await self.client._request("POST", "/api/git/review/create-pr", body={"path": path})

    async def branches(self, path: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request("GET", "/api/git/branches", query={"path": path}))

    async def switch(self, path: str, branch: str) -> Any:
        return await self.client._request("POST", "/api/git/branch/switch", body={"path": path, "branch": branch})

    async def worktrees(self, path: str) -> DesktopWorktreeList:
        return cast(DesktopWorktreeList, await self.client._request("GET", "/api/git/worktrees", query={"path": path}))

    async def add_worktree(self, path: str, options: DesktopWorktreeOptions) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request("POST", "/api/git/worktree/add", body={**options, "path": path}))

    async def remove_worktree(self, path: str, worktree_path: str, *, force: bool = False) -> Any:
        return await self.client._request("POST", "/api/git/worktree/remove", body={"path": path, "worktreePath": worktree_path, "force": force})


class DesktopSkill(TypedDict, total=False):
    name: str
    description: str
    path: str
    category: str
    enabled: bool
    source: str
    usage: int
    provenance: Literal['hub', 'bundled', 'external', 'agent']


class SkillContent(TypedDict):
    name: str
    content: str
    path: str


class HubSkill(TypedDict, total=False):
    identifier: str
    name: str
    description: str
    source: str
    trust_level: str
    repo: str | None
    tags: list[str]
    installed: bool
    category: str
    skill_md: str
    files: list[str]


class HubSearch(TypedDict):
    results: list[HubSkill]
    source_counts: dict[str, int]
    timed_out: list[str]
    installed: dict[str, dict[str, str | None]]


class HubScan(TypedDict, total=False):
    name: str
    identifier: str
    source: str
    trust_level: str
    verdict: str
    summary: str
    policy: Literal['allow', 'ask', 'block']
    policy_reason: str
    findings: list[dict[str, Any]]
    severity_counts: dict[str, int]
    tier1: dict[str, Any] | None


class SkillProcessReceipt(TypedDict):
    ok: bool
    pid: int
    name: str


class DesktopSkills:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def list(self) -> builtins.list[DesktopSkill]:
        result = await self.client._request("GET", "/api/skills")
        return cast(builtins.list[DesktopSkill], result)

    async def content(self, name: str) -> SkillContent:
        return cast(SkillContent, await self.client._request("GET", "/api/skills/content", query={"name": name}))

    async def save(self, name: str, content: str) -> Any:
        return await self.client._request("PUT", "/api/skills/content", body={"name": name, "content": content})

    async def create(self, name: str, content: str, *, category: str | None = None) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('POST', '/api/skills', body={'name': name, 'content': content, 'category': category}))

    async def toggle(self, name: str, enabled: bool) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('PUT', '/api/skills/toggle', body={'name': name, 'enabled': enabled}))

    async def official(self) -> builtins.list[HubSkill]:
        result = await self.client._request('GET', '/api/skills/hub/official')
        return cast(builtins.list[HubSkill], result['skills'])

    async def sources(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/skills/hub/sources'))

    async def search(self, query: str, *, source: str = 'all', limit: int = 20) -> HubSearch:
        if not 1 <= limit <= 50:
            raise ValueError('Skill search limit must be between 1 and 50')
        return cast(HubSearch, await self.client._request('GET', '/api/skills/hub/search', query={'q': query, 'source': source, 'limit': limit}, timeout=45))

    async def preview(self, identifier: str) -> HubSkill:
        return cast(HubSkill, await self.client._request('GET', '/api/skills/hub/preview', query={'identifier': identifier}))

    async def scan(self, identifier: str) -> HubScan:
        return cast(HubScan, await self.client._request('GET', '/api/skills/hub/scan', query={'identifier': identifier}, timeout=90))

    async def install(self, identifier: str) -> SkillProcessReceipt:
        """Start the native installer. This receipt is not installation success."""
        return cast(SkillProcessReceipt, await self.client._request('POST', '/api/skills/hub/install', body={'identifier': identifier}))

    async def uninstall(self, name: str) -> SkillProcessReceipt:
        return cast(SkillProcessReceipt, await self.client._request('POST', '/api/skills/hub/uninstall', body={'name': name}))

    async def update(self) -> SkillProcessReceipt:
        """Hermes's update operation updates installed Hub skills as a batch."""
        return cast(SkillProcessReceipt, await self.client._request('POST', '/api/skills/hub/update', body={}))


class DesktopSessions:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def messages(self, session_id: str, *, limit: int = 100, order: Literal["latest", "oldest"] = "latest") -> dict[str, Any]:
        if not 1 <= limit <= 500:
            raise ValueError("Session history limit must be between 1 and 500")
        result = await self.client._request("GET", f"/api/sessions/{_segment(session_id)}/messages", query={"limit": limit, "order": order, "inline_images": "false"})
        if result.get("profile") != self.client.profile:
            raise ValueError("The returned history belongs to another profile")
        return cast(dict[str, Any], result)
