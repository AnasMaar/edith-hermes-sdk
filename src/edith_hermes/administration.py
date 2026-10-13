"""Native Desktop administration APIs, separate from control-plane auth.

Clients retain concrete profile scope. Local runtime and download resources are
host-wide in Hermes; their IDs must also carry the connection identity in apps.
No mutation is retried automatically and process/job receipts are not success.
"""
from __future__ import annotations

from typing import Any, Literal, TypedDict, cast

from typing_extensions import Required

from .desktop import AsyncHermesDesktop, _segment


class NativeResult(TypedDict, total=False):
    ok: bool
    message: str
    needs_restart: bool


class ValidationResult(NativeResult, total=False):
    reachable: bool
    models: list[str]


class NativeJobReceipt(TypedDict, total=False):
    job_id: str | None
    name: str
    pid: int
    already_downloaded: bool


class ModelAssignment(TypedDict, total=False):
    scope: Required[Literal['main', 'auxiliary']]
    provider: Required[str]
    model: Required[str]
    task: str
    reasoning_effort: str | None
    base_url: str
    api_key: str
    confirm_expensive_model: bool


class CustomEndpoint(TypedDict, total=False):
    id: str
    name: Required[str]
    base_url: Required[str]
    model: Required[str]
    api_key: str | None
    api_mode: Literal['', 'chat_completions', 'codex_responses', 'anthropic_messages'] | None
    context_length: int | None
    discover_models: bool
    make_default: bool
    models: list[str] | None


class ProviderLogin(TypedDict, total=False):
    session_id: str
    status: str
    verification_url: str
    user_code: str
    expires_in: int
    poll_interval: int
    expires_at: float
    error_message: str | None


class LearningNode(TypedDict, total=False):
    id: str
    content: str
    kind: str
    name: str
    source: str


class DesktopAdministration:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client
        self.providers = DesktopProviders(client)
        self.models = DesktopModelAdministration(client)
        self.local_models = DesktopLocalModels(client)
        self.memory = DesktopMemory(client)
        self.profiles = DesktopProfileTransfer(client)
        self.channels = DesktopChannels(client)


class DesktopProviders:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def keys(self) -> dict[str, Any]:
        """Native redacted inventory. Never round-trip this inventory as a write."""
        return cast(dict[str, Any], await self.client._request('GET', '/api/env'))

    async def set_key(self, key: str, value: str) -> NativeResult:
        return cast(NativeResult, await self.client._request('PUT', '/api/env', body={
            'key': key, 'value': value, 'profile': self.client.profile, 'provider_setup': True}))

    async def test_key(self, key: str, value: str, *, api_key: str = '') -> ValidationResult:
        return cast(ValidationResult, await self.client._request('POST', '/api/providers/validate', body={
            'key': key, 'value': value, 'api_key': api_key, 'profile': self.client.profile}))

    async def remove_key(self, key: str) -> NativeResult:
        return cast(NativeResult, await self.client._request('DELETE', '/api/env', body={'key': key, 'profile': self.client.profile}))

    async def oauth_catalog(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/providers/oauth'))

    async def start_login(self, provider: str) -> ProviderLogin:
        return cast(ProviderLogin, await self.client._request('POST', '/api/providers/oauth/'+_segment(provider)+'/start'))

    async def login(self, provider: str, session_id: str) -> ProviderLogin:
        return cast(ProviderLogin, await self.client._request('GET', '/api/providers/oauth/'+_segment(provider)+'/poll/'+_segment(session_id)))

    async def cancel_login(self, session_id: str) -> NativeResult:
        return cast(NativeResult, await self.client._request('DELETE', '/api/providers/oauth/sessions/'+_segment(session_id)))

    async def disconnect(self, provider: str) -> NativeResult:
        return cast(NativeResult, await self.client._request('DELETE', '/api/providers/oauth/'+_segment(provider)))

    async def endpoints(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/providers/custom-endpoints'))

    async def save_endpoint(self, endpoint: CustomEndpoint) -> NativeResult:
        return cast(NativeResult, await self.client._request('POST', '/api/providers/custom-endpoints', body=endpoint))

    async def test_endpoint(self, endpoint: CustomEndpoint) -> ValidationResult:
        return cast(ValidationResult, await self.client._request('POST', '/api/providers/custom-endpoints/validate', body=endpoint))

    async def activate_endpoint(self, identity: str) -> NativeResult:
        return cast(NativeResult, await self.client._request('POST', '/api/providers/custom-endpoints/'+_segment(identity)+'/activate'))

    async def remove_endpoint(self, identity: str) -> NativeResult:
        return cast(NativeResult, await self.client._request('DELETE', '/api/providers/custom-endpoints/'+_segment(identity)))


class DesktopModelAdministration:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def auxiliary(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/model/auxiliary'))

    async def assign(self, assignment: ModelAssignment) -> dict[str, Any]:
        """Writes defaults for new sessions. An ok:false confirmation is not a save."""
        return cast(dict[str, Any], await self.client._request('POST', '/api/model/set', body=assignment))


class DesktopLocalModels:
    """Host-wide engine/jobs; activation writes the client's profile default."""
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def status(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/local-models/status'))

    async def hardware(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/local-models/hardware'))

    async def catalog(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/local-models/catalog'))

    async def install_runtime(self, backend: str | None = None) -> NativeJobReceipt:
        return cast(NativeJobReceipt, await self.client._request('POST', '/api/local-models/runtime/install', body={'backend': backend}))

    async def download(self, model_id: str) -> NativeJobReceipt:
        return cast(NativeJobReceipt, await self.client._request('POST', '/api/local-models/download', body={'model_id': model_id}))

    async def jobs(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/local-models/jobs'))

    async def job(self, identity: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/local-models/jobs/'+_segment(identity)))

    async def pause_download(self, identity: str) -> NativeResult:
        return cast(NativeResult, await self.client._request('POST', '/api/local-models/download/pause', body={'job_id': identity}))

    async def resume_download(self, identity: str) -> NativeResult:
        return cast(NativeResult, await self.client._request('POST', '/api/local-models/download/resume', body={'job_id': identity}))

    async def activate(self, model_id: str) -> NativeJobReceipt:
        return cast(NativeJobReceipt, await self.client._request('POST', '/api/local-models/activate', body={'model_id': model_id}))

    async def eject(self, model_id: str) -> NativeResult:
        return cast(NativeResult, await self.client._request('POST', '/api/local-models/eject', body={'model_id': model_id}, timeout=180))

    async def server(self, action: Literal['start', 'stop']) -> NativeResult:
        if action not in {'start', 'stop'}:
            raise ValueError('Select a native runtime action')
        return cast(NativeResult, await self.client._request('POST', '/api/local-models/server', body={'action': action}, timeout=180))

    async def remove(self, model_id: str) -> NativeResult:
        return cast(NativeResult, await self.client._request('DELETE', '/api/local-models/models/'+_segment(model_id)))


class DesktopMemory:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def status(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/memory'))

    async def graph(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/learning/graph'))

    async def node(self, identity: str) -> LearningNode:
        return cast(LearningNode, await self.client._request('GET', '/api/learning/node', query={'id': identity}))

    async def save_node(self, identity: str, content: str) -> NativeResult:
        """Fingerprint-bearing memory IDs provide native stale-target rejection."""
        if not identity.startswith('memory:') or len(identity.split(':')) != 4:
            raise ValueError('Use a fingerprinted native memory identity for safe editing')
        return cast(NativeResult, await self.client._request('PUT', '/api/learning/node', body={'id': identity, 'content': content, 'profile': self.client.profile}))

    async def remove_node(self, identity: str) -> NativeResult:
        if not identity.startswith('memory:') or len(identity.split(':')) != 4:
            raise ValueError('Use a fingerprinted native memory identity for safe removal')
        return cast(NativeResult, await self.client._request('DELETE', '/api/learning/node', body={'id': identity, 'profile': self.client.profile}))

    async def usage(self, days: int = 30) -> dict[str, Any]:
        """Keep estimated/actual costs and native token categories distinct."""
        if not 1 <= days <= 365:
            raise ValueError('Usage days must be between 1 and 365')
        return cast(dict[str, Any], await self.client._request('GET', '/api/analytics/usage', query={'days': days}))


class DesktopProfileTransfer:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def export(self, *, output: str | None = None) -> NativeJobReceipt:
        return cast(NativeJobReceipt, await self.client._request('POST', '/api/ops/backup', body={'output': output}))

    async def restore(self, archive: str, *, force: bool = False) -> NativeJobReceipt:
        return cast(NativeJobReceipt, await self.client._request('POST', '/api/ops/import', body={'archive': archive, 'force': force}))

    async def action(self, name: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/actions/'+_segment(name)+'/status'))


class ChannelUpdate(TypedDict, total=False):
    enabled: bool
    env: dict[str, str]
    clear_env: list[str]


class DesktopChannels:
    def __init__(self, client: AsyncHermesDesktop):
        self.client = client

    async def list(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.client._request('GET', '/api/messaging/platforms'))

    async def save(self, platform: str, changes: ChannelUpdate) -> NativeResult:
        """Send changed credential fields only; inventory is redacted."""
        return cast(NativeResult, await self.client._request('PUT', '/api/messaging/platforms/'+_segment(platform), body={**changes, 'profile': self.client.profile}))

    async def test(self, platform: str) -> ValidationResult:
        return cast(ValidationResult, await self.client._request('POST', '/api/messaging/platforms/'+_segment(platform)+'/test'))
