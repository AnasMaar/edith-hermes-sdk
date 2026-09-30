"""Generated typed convenience resources. Do not edit; run scripts/generate_sdk.py."""
from __future__ import annotations
import builtins
import typing
from collections.abc import AsyncIterator, Mapping
from contextlib import AbstractAsyncContextManager
from typing import Any, Literal, Union
from ..duplex import NativeConnection, connect
from ..resources import Resource, UNSET, Unset, payload as _payload
from . import types_control_plane as _types_control_plane
from . import types_images as _types_images
from . import types_runtime as _types_runtime
from . import types_tools as _types_tools
from . import types_inference as _types_inference
from . import types_native as _types_native

class BindingResource(Resource):
    async def get(self) -> _types_tools.ToolBinding:
        return typing.cast('_types_tools.ToolBinding', await self._invoke('getToolBinding', _payload({})))

    async def delete(self) -> Any:
        return await self._invoke('deleteToolBinding', _payload({}))


class BindingsResource(Resource):
    async def list(self, *, instance_id: str | Unset = UNSET, profile_id: str | Unset = UNSET, session_id: str | Unset = UNSET) -> _types_tools.listToolBindingsResult:
        return typing.cast('_types_tools.listToolBindingsResult', await self._invoke('listToolBindings', _payload({'instance_id': instance_id, 'profile_id': profile_id, 'session_id': session_id})))

    async def create(self, *, bundle_id: str, scope: _types_tools.BindingScope, enabled_tools: builtins.list[str] | Unset = UNSET, approval_policy: Literal['always', 'on_dangerous', 'never'] | Unset = UNSET, priority: int | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_tools.ToolBinding:
        body = _payload({'bundleId': bundle_id, 'scope': scope, 'enabledTools': enabled_tools, 'approvalPolicy': approval_policy, 'priority': priority}, extra_body)
        return typing.cast('_types_tools.ToolBinding', await self._invoke('createToolBinding', _payload({'body': body})))

    def __call__(self, binding_id: str) -> BindingResource:
        if not binding_id:
            raise ValueError('Resource ID must not be empty')
        return BindingResource(self._sdk, **{**self._scope, 'binding_id': binding_id})


class BuildResource(Resource):
    async def get(self) -> _types_images.ImageBuild:
        return typing.cast('_types_images.ImageBuild', await self._invoke('getImageBuild', _payload({})))

    async def cancel(self) -> Any:
        return await self._invoke('cancelImageBuild', _payload({}))

    def logs(self, *, after: str | Unset = UNSET) -> AsyncIterator[dict[str, Any]]:
        return self._stream('streamImageBuildLogs', _payload({'after': after}))

    async def wait(self, *, timeout: float = 300, poll_interval: float = 0.5) -> _types_images.ImageBuild:
        return typing.cast('_types_images.ImageBuild', await self._wait('getImageBuild', 'status', set(['succeeded', 'failed', 'cancelled']), timeout=timeout, poll_interval=poll_interval))


class BuildsResource(Resource):
    async def list(self, *, owner_id: str | Unset = UNSET, status: _types_images.BuildStatus | Unset = UNSET) -> _types_images.ImageBuildPage:
        return typing.cast('_types_images.ImageBuildPage', await self._invoke('listImageBuilds', _payload({'owner_id': owner_id, 'status': status})))

    async def start(self, *, idempotency_key: str | Unset = UNSET, owner: _types_images.OwnerReference, source: Union[_types_images.startImageBuildSource0, _types_images.startImageBuildSource1], destination: _types_images.startImageBuildDestination, build_secret_refs: builtins.list[str] | Unset = UNSET, cache_policy: Literal['use', 'refresh', 'disabled'] | Unset = UNSET, verification_policy: Literal['required', 'warn', 'disabled'] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_images.ImageBuild:
        body = _payload({'owner': owner, 'source': source, 'destination': destination, 'buildSecretRefs': build_secret_refs, 'cachePolicy': cache_policy, 'verificationPolicy': verification_policy}, extra_body)
        return typing.cast('_types_images.ImageBuild', await self._invoke('startImageBuild', _payload({'idempotency_key': idempotency_key, 'body': body})))

    def __call__(self, build_id: str) -> BuildResource:
        if not build_id:
            raise ValueError('Resource ID must not be empty')
        return BuildResource(self._sdk, **{**self._scope, 'build_id': build_id})


class BundleResource(Resource):
    async def get(self) -> _types_tools.ToolBundle:
        return typing.cast('_types_tools.ToolBundle', await self._invoke('getToolBundle', _payload({})))

    async def replace(self, *, name: str, description: str | Unset = UNSET, transport: Literal['callback', 'mcp'], callback: _types_tools.CallbackTransport | Unset = UNSET, mcp_server_id: str | Unset = UNSET, tools: builtins.list[_types_tools.ToolDefinition] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_tools.ToolBundle:
        body = _payload({'name': name, 'description': description, 'transport': transport, 'callback': callback, 'mcpServerId': mcp_server_id, 'tools': tools}, extra_body)
        return typing.cast('_types_tools.ToolBundle', await self._invoke('replaceToolBundle', _payload({'body': body})))

    async def delete(self) -> Any:
        return await self._invoke('deleteToolBundle', _payload({}))


class BundlesResource(Resource):
    async def list(self) -> _types_tools.listToolBundlesResult:
        return typing.cast('_types_tools.listToolBundlesResult', await self._invoke('listToolBundles', _payload({})))

    async def create(self, *, name: str, description: str | Unset = UNSET, transport: Literal['callback', 'mcp'], callback: _types_tools.CallbackTransport | Unset = UNSET, mcp_server_id: str | Unset = UNSET, tools: builtins.list[_types_tools.ToolDefinition] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_tools.ToolBundle:
        body = _payload({'name': name, 'description': description, 'transport': transport, 'callback': callback, 'mcpServerId': mcp_server_id, 'tools': tools}, extra_body)
        return typing.cast('_types_tools.ToolBundle', await self._invoke('createToolBundle', _payload({'body': body})))

    def __call__(self, bundle_id: str) -> BundleResource:
        if not bundle_id:
            raise ValueError('Resource ID must not be empty')
        return BundleResource(self._sdk, **{**self._scope, 'bundle_id': bundle_id})


class ImageResource(Resource):
    async def get(self) -> _types_images.ManagedImage:
        return typing.cast('_types_images.ManagedImage', await self._invoke('getManagedImage', _payload({})))

    async def delete(self) -> Any:
        return await self._invoke('deleteManagedImage', _payload({}))


class ImagesResource(Resource):
    async def list(self, *, owner_id: str | Unset = UNSET, usable: bool | Unset = UNSET) -> _types_images.ManagedImagePage:
        return typing.cast('_types_images.ManagedImagePage', await self._invoke('listManagedImages', _payload({'owner_id': owner_id, 'usable': usable})))

    @property
    def recipes(self) -> RecipesResource:
        return RecipesResource(self._sdk, **self._scope)

    @property
    def builds(self) -> BuildsResource:
        return BuildsResource(self._sdk, **self._scope)

    def __call__(self, image_id: str) -> ImageResource:
        if not image_id:
            raise ValueError('Resource ID must not be empty')
        return ImageResource(self._sdk, **{**self._scope, 'image_id': image_id})


class InferenceResource(Resource):
    async def chat(self, *, model: str, messages: builtins.list[_types_inference.createChatCompletionMessagesItem], temperature: float | Unset = UNSET, max_tokens: int | Unset = UNSET, stream: bool | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_inference.createChatCompletionResult:
        body = _payload({'model': model, 'messages': messages, 'temperature': temperature, 'max_tokens': max_tokens, 'stream': stream}, extra_body)
        return typing.cast('_types_inference.createChatCompletionResult', await self._invoke('createChatCompletion', _payload({'body': body})))

    async def complete(self, *, model: str, prompt: str, max_tokens: int | Unset = UNSET, temperature: float | Unset = UNSET, stream: bool | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_inference.createCompletionResult:
        body = _payload({'model': model, 'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature, 'stream': stream}, extra_body)
        return typing.cast('_types_inference.createCompletionResult', await self._invoke('createCompletion', _payload({'body': body})))


class InstanceResource(Resource):
    async def get(self) -> _types_control_plane.Instance:
        return typing.cast('_types_control_plane.Instance', await self._invoke('getInstance', _payload({})))

    async def update(self, *, if_match: str, name: str | Unset = UNSET, desired_state: _types_control_plane.DesiredState | Unset = UNSET, labels: dict[str, str] | Unset = UNSET, runtime: _types_control_plane.RuntimeSpec | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_control_plane.Instance:
        body = _payload({'name': name, 'desiredState': desired_state, 'labels': labels, 'runtime': runtime}, extra_body)
        return typing.cast('_types_control_plane.Instance', await self._invoke('updateInstance', _payload({'if_match': if_match, 'body': body})))

    async def delete(self, *, retain_data: bool | Unset = UNSET) -> _types_control_plane.InstanceOperation:
        return typing.cast('_types_control_plane.InstanceOperation', await self._invoke('deleteInstance', _payload({'retain_data': retain_data})))

    async def action(self, *, action: Literal['start', 'stop', 'restart', 'reconcile'], idempotency_key: str | Unset = UNSET) -> _types_control_plane.InstanceOperation:
        return typing.cast('_types_control_plane.InstanceOperation', await self._invoke('changeInstanceState', _payload({'action': action, 'idempotency_key': idempotency_key})))

    async def connection(self) -> _types_control_plane.ConnectionDescriptor:
        return typing.cast('_types_control_plane.ConnectionDescriptor', await self._invoke('getInstanceConnection', _payload({})))

    async def capabilities(self) -> _types_control_plane.CapabilityDocument:
        return typing.cast('_types_control_plane.CapabilityDocument', await self._invoke('getInstanceCapabilities', _payload({})))

    async def runtime_capabilities(self) -> _types_runtime.RuntimeCapabilities:
        return typing.cast('_types_runtime.RuntimeCapabilities', await self._invoke('getInstanceRuntimeCapabilities', _payload({})))

    @property
    def profiles(self) -> ProfilesResource:
        return ProfilesResource(self._sdk, **self._scope)


class InstancesResource(Resource):
    async def list(self, *, cursor: str | Unset = UNSET, limit: int | Unset = UNSET, owner_id: str | Unset = UNSET, pool_id: str | Unset = UNSET, status: _types_control_plane.InstanceStatus | Unset = UNSET) -> _types_control_plane.InstancePage:
        return typing.cast('_types_control_plane.InstancePage', await self._invoke('listInstances', _payload({'cursor': cursor, 'limit': limit, 'owner_id': owner_id, 'pool_id': pool_id, 'status': status})))

    async def create(self, *, idempotency_key: str | Unset = UNSET, owner: _types_control_plane.OwnerReference, name: str, runtime: _types_control_plane.RuntimeSpec, pool_id: str | Unset = UNSET, labels: dict[str, str] | Unset = UNSET, bootstrap: _types_control_plane.BootstrapSpec | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_control_plane.InstanceOperation:
        body = _payload({'owner': owner, 'name': name, 'runtime': runtime, 'poolId': pool_id, 'labels': labels, 'bootstrap': bootstrap}, extra_body)
        return typing.cast('_types_control_plane.InstanceOperation', await self._invoke('createInstance', _payload({'idempotency_key': idempotency_key, 'body': body})))

    def __call__(self, instance_id: str) -> InstanceResource:
        if not instance_id:
            raise ValueError('Resource ID must not be empty')
        return InstanceResource(self._sdk, **{**self._scope, 'instance_id': instance_id})


class JobResource(Resource):
    async def get(self) -> _types_control_plane.ProvisioningJob:
        return typing.cast('_types_control_plane.ProvisioningJob', await self._invoke('getProvisioningJob', _payload({})))

    async def wait(self, *, timeout: float = 300, poll_interval: float = 0.5) -> _types_control_plane.ProvisioningJob:
        return typing.cast('_types_control_plane.ProvisioningJob', await self._wait('getProvisioningJob', 'phase', set(['ready', 'failed', 'cancelled']), timeout=timeout, poll_interval=poll_interval))


class JobsResource(Resource):
    async def create(self, *, idempotency_key: str | Unset = UNSET, owner: _types_control_plane.OwnerReference, name: str, image: Union[_types_control_plane.provisionUserInstanceImage0, _types_control_plane.provisionUserInstanceImage1] | Unset = UNSET, runtime: _types_control_plane.provisionUserInstanceRuntime, bootstrap: _types_control_plane.BootstrapSpec | Unset = UNSET, labels: dict[str, str] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_control_plane.ProvisioningJob:
        body = _payload({'owner': owner, 'name': name, 'image': image, 'runtime': runtime, 'bootstrap': bootstrap, 'labels': labels}, extra_body)
        return typing.cast('_types_control_plane.ProvisioningJob', await self._invoke('provisionUserInstance', _payload({'idempotency_key': idempotency_key, 'body': body})))

    def __call__(self, job_id: str) -> JobResource:
        if not job_id:
            raise ValueError('Resource ID must not be empty')
        return JobResource(self._sdk, **{**self._scope, 'job_id': job_id})


class LeaseResource(Resource):
    async def release(self) -> Any:
        return await self._invoke('releaseInstanceLease', _payload({}))


class LeasesResource(Resource):
    async def acquire(self, *, idempotency_key: str | Unset = UNSET, sticky_key: str | Unset = UNSET, ttl_seconds: int | Unset = UNSET, required_labels: dict[str, str] | Unset = UNSET, profile: Union[_types_control_plane.acquireInstanceLeaseProfile0, _types_control_plane.CreateProfileRequest] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_control_plane.InstanceLease:
        body = _payload({'stickyKey': sticky_key, 'ttlSeconds': ttl_seconds, 'requiredLabels': required_labels, 'profile': profile}, extra_body)
        return typing.cast('_types_control_plane.InstanceLease', await self._invoke('acquireInstanceLease', _payload({'idempotency_key': idempotency_key, 'body': body})))

    def __call__(self, lease_id: str) -> LeaseResource:
        if not lease_id:
            raise ValueError('Resource ID must not be empty')
        return LeaseResource(self._sdk, **{**self._scope, 'lease_id': lease_id})


class McpServerResource(Resource):
    async def get(self) -> _types_tools.McpServer:
        return typing.cast('_types_tools.McpServer', await self._invoke('getMcpServer', _payload({})))

    async def replace(self, *, name: str, transport: Literal['stdio', 'streamable_http', 'sse'], command: str | Unset = UNSET, args: builtins.list[str] | Unset = UNSET, url: str | Unset = UNSET, headers: dict[str, str] | Unset = UNSET, auth: Literal['oauth'] | Unset = UNSET, environment: dict[str, str] | Unset = UNSET, secret_refs: dict[str, str] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_tools.McpServer:
        body = _payload({'name': name, 'transport': transport, 'command': command, 'args': args, 'url': url, 'headers': headers, 'auth': auth, 'environment': environment, 'secretRefs': secret_refs}, extra_body)
        return typing.cast('_types_tools.McpServer', await self._invoke('replaceMcpServer', _payload({'body': body})))

    async def delete(self) -> Any:
        return await self._invoke('deleteMcpServer', _payload({}))

    async def action(self, *, type: Literal['test', 'reload', 'begin_oauth', 'poll_oauth', 'complete_oauth', 'cancel_oauth'], binding_id: str | Unset = UNSET, session_id: str | Unset = UNSET, client_redirect_uri: str | Unset = UNSET, code: str | Unset = UNSET, state: str | Unset = UNSET, error: str | Unset = UNSET, issuer: str | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> dict[str, Any]:
        body = _payload({'type': type, 'bindingId': binding_id, 'sessionId': session_id, 'clientRedirectUri': client_redirect_uri, 'code': code, 'state': state, 'error': error, 'issuer': issuer}, extra_body)
        return typing.cast('dict[str, Any]', await self._invoke('actOnMcpServer', _payload({'body': body})))


class McpServersResource(Resource):
    async def list(self) -> _types_tools.listMcpServersResult:
        return typing.cast('_types_tools.listMcpServersResult', await self._invoke('listMcpServers', _payload({})))

    async def create(self, *, name: str, transport: Literal['stdio', 'streamable_http', 'sse'], command: str | Unset = UNSET, args: builtins.list[str] | Unset = UNSET, url: str | Unset = UNSET, headers: dict[str, str] | Unset = UNSET, auth: Literal['oauth'] | Unset = UNSET, environment: dict[str, str] | Unset = UNSET, secret_refs: dict[str, str] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_tools.McpServer:
        body = _payload({'name': name, 'transport': transport, 'command': command, 'args': args, 'url': url, 'headers': headers, 'auth': auth, 'environment': environment, 'secretRefs': secret_refs}, extra_body)
        return typing.cast('_types_tools.McpServer', await self._invoke('createMcpServer', _payload({'body': body})))

    def __call__(self, server_id: str) -> McpServerResource:
        if not server_id:
            raise ValueError('Resource ID must not be empty')
        return McpServerResource(self._sdk, **{**self._scope, 'server_id': server_id})


class NativeResource(Resource):
    async def ping(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.PingResult:
        'Cheapest liveness probe; answered on the WS reader thread even while every agent is mid-turn.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PingResult', await self._native('ping', params))

    @property
    def agents(self) -> NativeAgentsResource:
        return NativeAgentsResource(self._sdk, **self._scope)

    @property
    def approval(self) -> NativeApprovalResource:
        return NativeApprovalResource(self._sdk, **self._scope)

    @property
    def billing(self) -> NativeBillingResource:
        return NativeBillingResource(self._sdk, **self._scope)

    @property
    def bot_relay(self) -> NativeBotRelayResource:
        return NativeBotRelayResource(self._sdk, **self._scope)

    @property
    def browser(self) -> NativeBrowserResource:
        return NativeBrowserResource(self._sdk, **self._scope)

    @property
    def clarify(self) -> NativeClarifyResource:
        return NativeClarifyResource(self._sdk, **self._scope)

    @property
    def cli(self) -> NativeCliResource:
        return NativeCliResource(self._sdk, **self._scope)

    @property
    def client(self) -> NativeClientResource:
        return NativeClientResource(self._sdk, **self._scope)

    @property
    def clipboard(self) -> NativeClipboardResource:
        return NativeClipboardResource(self._sdk, **self._scope)

    @property
    def command(self) -> NativeCommandResource:
        return NativeCommandResource(self._sdk, **self._scope)

    @property
    def commands(self) -> NativeCommandsResource:
        return NativeCommandsResource(self._sdk, **self._scope)

    @property
    def complete(self) -> NativeCompleteResource:
        return NativeCompleteResource(self._sdk, **self._scope)

    @property
    def config(self) -> NativeConfigResource:
        return NativeConfigResource(self._sdk, **self._scope)

    @property
    def connection(self) -> NativeConnectionResource:
        return NativeConnectionResource(self._sdk, **self._scope)

    @property
    def connectors(self) -> NativeConnectorsResource:
        return NativeConnectorsResource(self._sdk, **self._scope)

    @property
    def cron(self) -> NativeCronResource:
        return NativeCronResource(self._sdk, **self._scope)

    @property
    def delegation(self) -> NativeDelegationResource:
        return NativeDelegationResource(self._sdk, **self._scope)

    @property
    def diagnostics(self) -> NativeDiagnosticsResource:
        return NativeDiagnosticsResource(self._sdk, **self._scope)

    @property
    def file(self) -> NativeFileResource:
        return NativeFileResource(self._sdk, **self._scope)

    @property
    def free_tier(self) -> NativeFreeTierResource:
        return NativeFreeTierResource(self._sdk, **self._scope)

    @property
    def gateway(self) -> NativeGatewayResource:
        return NativeGatewayResource(self._sdk, **self._scope)

    @property
    def groups(self) -> NativeGroupsResource:
        return NativeGroupsResource(self._sdk, **self._scope)

    @property
    def handoff(self) -> NativeHandoffResource:
        return NativeHandoffResource(self._sdk, **self._scope)

    @property
    def image(self) -> NativeImageResource:
        return NativeImageResource(self._sdk, **self._scope)

    @property
    def input(self) -> NativeInputResource:
        return NativeInputResource(self._sdk, **self._scope)

    @property
    def insights(self) -> NativeInsightsResource:
        return NativeInsightsResource(self._sdk, **self._scope)

    @property
    def learning(self) -> NativeLearningResource:
        return NativeLearningResource(self._sdk, **self._scope)

    @property
    def llm(self) -> NativeLlmResource:
        return NativeLlmResource(self._sdk, **self._scope)

    @property
    def mcp(self) -> NativeMcpResource:
        return NativeMcpResource(self._sdk, **self._scope)

    @property
    def message(self) -> NativeMessageResource:
        return NativeMessageResource(self._sdk, **self._scope)

    @property
    def model(self) -> NativeModelResource:
        return NativeModelResource(self._sdk, **self._scope)

    @property
    def paste(self) -> NativePasteResource:
        return NativePasteResource(self._sdk, **self._scope)

    @property
    def pdf(self) -> NativePdfResource:
        return NativePdfResource(self._sdk, **self._scope)

    @property
    def pet(self) -> NativePetResource:
        return NativePetResource(self._sdk, **self._scope)

    @property
    def plugins(self) -> NativePluginsResource:
        return NativePluginsResource(self._sdk, **self._scope)

    @property
    def preview(self) -> NativePreviewResource:
        return NativePreviewResource(self._sdk, **self._scope)

    @property
    def process(self) -> NativeProcessResource:
        return NativeProcessResource(self._sdk, **self._scope)

    @property
    def profiles(self) -> NativeProfilesResource:
        return NativeProfilesResource(self._sdk, **self._scope)

    @property
    def project(self) -> NativeProjectResource:
        return NativeProjectResource(self._sdk, **self._scope)

    @property
    def projects(self) -> NativeProjectsResource:
        return NativeProjectsResource(self._sdk, **self._scope)

    @property
    def prompt(self) -> NativePromptResource:
        return NativePromptResource(self._sdk, **self._scope)

    @property
    def reload(self) -> NativeReloadResource:
        return NativeReloadResource(self._sdk, **self._scope)

    @property
    def request(self) -> NativeRequestResource:
        return NativeRequestResource(self._sdk, **self._scope)

    @property
    def rollback(self) -> NativeRollbackResource:
        return NativeRollbackResource(self._sdk, **self._scope)

    @property
    def session(self) -> NativeSessionResource:
        return NativeSessionResource(self._sdk, **self._scope)

    @property
    def setup(self) -> NativeSetupResource:
        return NativeSetupResource(self._sdk, **self._scope)

    @property
    def shell(self) -> NativeShellResource:
        return NativeShellResource(self._sdk, **self._scope)

    @property
    def skills(self) -> NativeSkillsResource:
        return NativeSkillsResource(self._sdk, **self._scope)

    @property
    def slash(self) -> NativeSlashResource:
        return NativeSlashResource(self._sdk, **self._scope)

    @property
    def spawn_tree(self) -> NativeSpawnTreeResource:
        return NativeSpawnTreeResource(self._sdk, **self._scope)

    @property
    def subagent(self) -> NativeSubagentResource:
        return NativeSubagentResource(self._sdk, **self._scope)

    @property
    def subscription(self) -> NativeSubscriptionResource:
        return NativeSubscriptionResource(self._sdk, **self._scope)

    @property
    def system(self) -> NativeSystemResource:
        return NativeSystemResource(self._sdk, **self._scope)

    @property
    def terminal(self) -> NativeTerminalResource:
        return NativeTerminalResource(self._sdk, **self._scope)

    @property
    def tools(self) -> NativeToolsResource:
        return NativeToolsResource(self._sdk, **self._scope)

    @property
    def toolsets(self) -> NativeToolsetsResource:
        return NativeToolsetsResource(self._sdk, **self._scope)

    @property
    def usage(self) -> NativeUsageResource:
        return NativeUsageResource(self._sdk, **self._scope)

    @property
    def vault(self) -> NativeVaultResource:
        return NativeVaultResource(self._sdk, **self._scope)

    @property
    def verification(self) -> NativeVerificationResource:
        return NativeVerificationResource(self._sdk, **self._scope)

    @property
    def voice(self) -> NativeVoiceResource:
        return NativeVoiceResource(self._sdk, **self._scope)

    @property
    def wake(self) -> NativeWakeResource:
        return NativeWakeResource(self._sdk, **self._scope)


class NativeAgentsResource(Resource):
    async def list(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.AgentsListResult:
        'Registry-wide background process summary for ``/agents``.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.AgentsListResult', await self._native('agents.list', params))


class NativeApprovalResource(Resource):
    async def pending(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ApprovalPendingResult:
        'Replay the approvals still waiting on this session (reconnect / polling).'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ApprovalPendingResult', await self._native('approval.pending', params))

    async def received(self, *, session_id: str, request_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ApprovalReceivedResult:
        'Tell the backend the card is on screen, so its timeout clock starts.'
        params = _payload({'session_id': session_id, 'request_id': request_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ApprovalReceivedResult', await self._native('approval.received', params))

    async def respond(self, *, session_id: str, choice: Union[str, None] | Unset = UNSET, all: Union[bool, None] | Unset = UNSET, request_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ApprovalRespondResult:
        "Deliver the user's decision on a dangerous command (falls back to durable identity on a stale sid)."
        params = _payload({'session_id': session_id, 'choice': choice, 'all': all, 'request_id': request_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ApprovalRespondResult', await self._native('approval.respond', params))


class NativeBillingResource(Resource):
    async def auto_reload(self, *, enabled: bool | Unset = UNSET, threshold: Union[float, str, None] | Unset = UNSET, top_up_amount: Union[float, str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.BillingMutationResult:
        'Enable/disable auto top-up with its threshold and reload amount (billing:manage).'
        params = _payload({'enabled': enabled, 'threshold': threshold, 'top_up_amount': top_up_amount}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BillingMutationResult', await self._native('billing.auto_reload', params))

    async def charge(self, *, amount_usd: Union[float, str, None] | Unset = UNSET, idempotency_key: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.BillingChargeResult:
        'Start a one-off top-up charge (billing:manage, idempotent).'
        params = _payload({'amount_usd': amount_usd, 'idempotency_key': idempotency_key}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BillingChargeResult', await self._native('billing.charge', params))

    async def charge_status(self, *, charge_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.BillingChargeStatusResult:
        'Poll one charge by id.'
        params = _payload({'charge_id': charge_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BillingChargeStatusResult', await self._native('billing.charge_status', params))

    async def state(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.BillingStateResult:
        'Read-only billing view (no scope); the Nous free tier is answered locally without a portal call.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BillingStateResult', await self._native('billing.state', params))

    async def step_up(self, *, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.BillingStepUpResult:
        'Run the billing:manage device flow; the URL/code arrive via billing.step_up.verification.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BillingStepUpResult', await self._native('billing.step_up', params))


class NativeBotRelayResource(Resource):
    async def deliver(self, *, message: str, from_profile: Union[str, None] | Unset = UNSET, from_handle: Union[str, None] | Unset = UNSET, from_connection: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.BotRelayDeliverResult:
        'Deliver a relayed DM into a Bot Chat on this gateway and return the one-turn reply (blocking).'
        params = _payload({'message': message, 'from_profile': from_profile, 'from_handle': from_handle, 'from_connection': from_connection}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BotRelayDeliverResult', await self._native('bot_relay.deliver', params))

    async def reply(self, *, id: str, reply: Union[str, None] | Unset = UNSET, error: Union[str, None] | Unset = UNSET, reason: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.OkResult:
        'Write a relayed reply and/or typed error for an envelope so the sender-side waiter resolves.'
        params = _payload({'id': id, 'reply': reply, 'error': error, 'reason': reason}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.OkResult', await self._native('bot_relay.reply', params))

    @property
    def outbox(self) -> NativeBotRelayOutboxResource:
        return NativeBotRelayOutboxResource(self._sdk, **self._scope)

    @property
    def roster(self) -> NativeBotRelayRosterResource:
        return NativeBotRelayRosterResource(self._sdk, **self._scope)


class NativeBotRelayOutboxResource(Resource):
    async def drain(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.BotRelayOutboxDrainResult:
        'Atomically claim every pending cross-connection envelope queued on this gateway.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BotRelayOutboxDrainResult', await self._native('bot_relay.outbox.drain', params))


class NativeBotRelayRosterResource(Resource):
    async def sync(self, *, agents: Union[builtins.list[_types_native.RelayAgentRow], None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.BotRelayRosterSyncResult:
        "Replace this gateway's view of agents on other connections; answers the accepted row count."
        params = _payload({'agents': agents}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BotRelayRosterSyncResult', await self._native('bot_relay.roster.sync', params))


class NativeBrowserResource(Resource):
    async def manage(self, *, action: _types_native.BrowserAction | Unset = UNSET, url: Union[str, None] | Unset = UNSET, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.BrowserManageResult:
        'Inspect, attach to, or drop the CDP browser the tools use; ``messages`` narrate a connect.'
        params = _payload({'action': action, 'url': url, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BrowserManageResult', await self._native('browser.manage', params))

    @property
    def controller(self) -> NativeBrowserControllerResource:
        return NativeBrowserControllerResource(self._sdk, **self._scope)


class NativeBrowserControllerResource(Resource):
    async def detach(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.BrowserControllerDetachResult:
        'Hard-detach only the controller owned by this authenticated transport.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BrowserControllerDetachResult', await self._native('browser.controller.detach', params))

    async def heartbeat(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.OkResult:
        "Acknowledge a heartbeat only for this transport's own attached controller."
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.OkResult', await self._native('browser.controller.heartbeat', params))

    async def register(self, *, session_id: str, controller_id: str, browser_profile_id: str, capabilities: Union[builtins.list[str], None] | Unset = UNSET, protocol_version: Union[Any, None] | Unset = UNSET, principal_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.BrowserControllerRegisterResult:
        'Attach this connection as the browser controller for one session; fails closed (4403).'
        params = _payload({'session_id': session_id, 'controller_id': controller_id, 'browser_profile_id': browser_profile_id, 'capabilities': capabilities, 'protocol_version': protocol_version, 'principal_id': principal_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BrowserControllerRegisterResult', await self._native('browser.controller.register', params))

    async def result(self, *, session_id: str, command_id: str, ok: Union[Any, None] | Unset = UNSET, result: Union[Any, None] | Unset = UNSET, error: Union[Any, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.BrowserControllerResultResult:
        'Deliver one command result to the broker; accepted is false for unknown or settled command ids.'
        params = _payload({'session_id': session_id, 'command_id': command_id, 'ok': ok, 'result': result, 'error': error}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BrowserControllerResultResult', await self._native('browser.controller.result', params))


class NativeClarifyResource(Resource):
    async def lock(self, *, request_id: str, question_id: str, answer: Any | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ClarifyLockResult:
        'Lock one answer of a batch clarify request (editable until every question is locked).'
        params = _payload({'request_id': request_id, 'question_id': question_id, 'answer': answer}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ClarifyLockResult', await self._native('clarify.lock', params))


class NativeCliResource(Resource):
    async def exec(self, *, argv: builtins.list[str], timeout: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.CliExecResult:
        'Run ``hermes <argv>`` non-interactively and capture its output; ``blocked`` explains a refusal.'
        params = _payload({'argv': argv, 'timeout': timeout}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.CliExecResult', await self._native('cli.exec', params))


class NativeClientResource(Resource):
    async def capabilities(self, *, server_requests: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ClientCapabilitiesResult:
        'What the calling client handles, sent once per connection (after gateway.ready); returns the server→client request methods this backend may send.'
        params = _payload({'server_requests': server_requests}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ClientCapabilitiesResult', await self._native('client.capabilities', params))


class NativeClipboardResource(Resource):
    async def paste(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.AttachedImageResult:
        'Save the host clipboard image into the session and queue it for the next turn.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.AttachedImageResult', await self._native('clipboard.paste', params))


class NativeCommandResource(Resource):
    async def dispatch(self, *, name: str, arg: Union[str, None] | Unset = UNSET, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.CommandDispatchResult:
        'Run a quick/plugin/bundle/skill/built-in slash command and answer a structured directive.'
        params = _payload({'name': name, 'arg': arg, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.CommandDispatchResult', await self._native('command.dispatch', params))

    async def resolve(self, *, name: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.CommandResolveResult:
        'Canonical registry command for a name or alias.'
        params = _payload({'name': name}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.CommandResolveResult', await self._native('command.resolve', params))


class NativeCommandsResource(Resource):
    async def catalog(self, *, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.CommandsCatalogResult:
        'Categorized slash metadata (registry, quick, plugin, skill) for completion menus.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.CommandsCatalogResult', await self._native('commands.catalog', params))


class NativeCompleteResource(Resource):
    async def path(self, *, word: Union[str, None] | Unset = UNSET, cwd: Union[str, None] | Unset = UNSET, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.CompletionItemsResult:
        'Path / @-reference completions for the composer (files, folders, profiles, plugin providers).'
        params = _payload({'word': word, 'cwd': cwd, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.CompletionItemsResult', await self._native('complete.path', params))

    async def slash(self, *, text: Union[str, None] | Unset = UNSET, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.CompleteSlashResult:
        'Ranked slash-command / skill completions for a ``/`` token.'
        params = _payload({'text': text, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.CompleteSlashResult', await self._native('complete.slash', params))


class NativeConfigResource(Resource):
    async def get(self, *, key: str, cwd: Union[str, None] | Unset = UNSET, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ConfigGetResult:
        'Read one normalised config value (or the whole effective config) the way the UIs render it.'
        params = _payload({'key': key, 'cwd': cwd, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ConfigGetResult', await self._native('config.get', params))

    async def set(self, *, key: str, value: Any | Unset = UNSET, session_id: Union[str, None] | Unset = UNSET, scope: Union[str, None] | Unset = UNSET, confirm_expensive_model: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ConfigSetResult:
        'Change one config key (persisted or session-scoped) and read back the normalised value.'
        params = _payload({'key': key, 'value': value, 'session_id': session_id, 'scope': scope, 'confirm_expensive_model': confirm_expensive_model}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ConfigSetResult', await self._native('config.set', params))

    async def show(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.ConfigShowResult:
        'Masked, display-ready config summary (model / agent / environment rows).'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ConfigShowResult', await self._native('config.show', params))


class NativeConnectionResource(Resource):
    async def respond(self, *, session_id: str, op_id: str, result: _types_native.ConnectionAnswer, extra_params: Mapping[str, Any] | None = None) -> _types_native.ConnectionRespondResult:
        'Per-target outcomes from the card, and an optional Continue.'
        params = _payload({'session_id': session_id, 'op_id': op_id, 'result': result}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ConnectionRespondResult', await self._native('connection.respond', params))


class NativeConnectorsResource(Resource):
    async def connect(self, *, session_id: str, connectors: builtins.list[str], reconnect: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ConnectorsConnectResult:
        "Start (or re-initiate) authorization for named connectors on the session's connection operation."
        params = _payload({'session_id': session_id, 'connectors': connectors, 'reconnect': reconnect}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ConnectorsConnectResult', await self._native('connectors.connect', params))

    async def list(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ConnectorsListResult:
        'Connector catalog + connection state for one owned session (``available=False`` when the toolset is off).'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ConnectorsListResult', await self._native('connectors.list', params))

    @property
    def operation(self) -> NativeConnectorsOperationResource:
        return NativeConnectorsOperationResource(self._sdk, **self._scope)


class NativeConnectorsOperationResource(Resource):
    async def status(self, *, session_id: str, op_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ConnectionOperationStatus:
        'The current snapshot of one open operation on an owned session.'
        params = _payload({'session_id': session_id, 'op_id': op_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ConnectionOperationStatus', await self._native('connectors.operation.status', params))

    async def wake(self, *, session_id: str, op_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ConnectionWakeResult:
        'The browser leg came back (hermes://connections/done): read the accounts now, not at the next tick.'
        params = _payload({'session_id': session_id, 'op_id': op_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ConnectionWakeResult', await self._native('connectors.operation.wake', params))


class NativeCronResource(Resource):
    async def manage(self, *, action: _types_native.CronAction | Unset = UNSET, name: Union[str, None] | Unset = UNSET, include_disabled: Union[bool, str, None] | Unset = UNSET, schedule: Union[str, None] | Unset = UNSET, prompt: Union[str, None] | Unset = UNSET, repeat: Union[int, str, None] | Unset = UNSET, continuity: Union[bool, str, None] | Unset = UNSET, deliver: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.CronManageResult:
        'List/add/remove/pause/resume cron jobs in the (optionally profile-scoped) cron store.'
        params = _payload({'action': action, 'name': name, 'include_disabled': include_disabled, 'schedule': schedule, 'prompt': prompt, 'repeat': repeat, 'continuity': continuity, 'deliver': deliver}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.CronManageResult', await self._native('cron.manage', params))


class NativeDelegationResource(Resource):
    async def pause(self, *, paused: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.DelegationPauseResult:
        'Block/unblock NEW spawns globally (active children keep running); returns the new state.'
        params = _payload({'paused': paused}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.DelegationPauseResult', await self._native('delegation.pause', params))

    async def status(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.DelegationStatusResult:
        'Running subagent tree plus the spawn pause flag and limits.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.DelegationStatusResult', await self._native('delegation.status', params))


class NativeDiagnosticsResource(Resource):
    async def share_nous(self, *, error_context: Union[str, None] | Unset = UNSET, extra_files: Union[dict[str, str], None] | Unset = UNSET, log_lines: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.DiagnosticsShareNousResult:
        'Upload a force-redacted debug bundle to Nous-internal diagnostics storage.'
        params = _payload({'error_context': error_context, 'extra_files': extra_files, 'log_lines': log_lines}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.DiagnosticsShareNousResult', await self._native('diagnostics.share_nous', params))


class NativeFileResource(Resource):
    async def attach(self, *, session_id: str, path: Union[str, None] | Unset = UNSET, data_url: Union[str, None] | Unset = UNSET, name: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.FileAttachResult:
        'Stage a non-image file into the session workspace and hand back its @file: ref.'
        params = _payload({'session_id': session_id, 'path': path, 'data_url': data_url, 'name': name}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.FileAttachResult', await self._native('file.attach', params))


class NativeFreeTierResource(Resource):
    async def ack_notice(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.FreeTierAckNoticeResult:
        'Mark the one-time availability notice as shown on the free-tier identity.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.FreeTierAckNoticeResult', await self._native('free_tier.ack_notice', params))

    async def provision(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.FreeTierProvisionResult:
        'Explicit retry of the free-tier identity mint when the boot bootstrap could not create it.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.FreeTierProvisionResult', await self._native('free_tier.provision', params))

    async def status(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.FreeTierStatusResult:
        "Pure read of the focused profile's free-tier identity state (no network, no side effects)."
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.FreeTierStatusResult', await self._native('free_tier.status', params))


class NativeGatewayResource(Resource):
    async def capabilities(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.GatewayCapabilitiesResult:
        'What THIS build enforces (a client withholds a feature unless advertised).'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GatewayCapabilitiesResult', await self._native('gateway.capabilities', params))


class NativeGroupsResource(Resource):
    async def approve(self, *, room_id: str, member_id: str, task_id: str, execution_generation: int, choice: _types_native.ApprovalChoice, request_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsApproveResult:
        'Resolve one exact pending approval raised by a local or peer room member.'
        params = _payload({'room_id': room_id, 'member_id': member_id, 'task_id': task_id, 'execution_generation': execution_generation, 'choice': choice, 'request_id': request_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsApproveResult', await self._native('groups.approve', params))

    async def capabilities(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsCapabilitiesResult:
        'Describe the hosted-room protocol implemented by this gateway.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsCapabilitiesResult', await self._native('groups.capabilities', params))

    async def create(self, *, room_id: str, name: str, members: builtins.list[_types_native.RoomMemberInput], authority_gateway_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsCreateResult:
        "Create a hosted room idempotently; authority is this gateway's stable install identity."
        params = _payload({'room_id': room_id, 'name': name, 'members': members, 'authority_gateway_id': authority_gateway_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsCreateResult', await self._native('groups.create', params))

    async def demote(self, *, room_id: str, observed_gateway_id: str, observed_epoch: int, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsDemoteResult:
        "Fence this gateway's stale room authority against a proven newer epoch."
        params = _payload({'room_id': room_id, 'observed_gateway_id': observed_gateway_id, 'observed_epoch': observed_epoch}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsDemoteResult', await self._native('groups.demote', params))

    async def disband(self, *, room_id: str, cancel_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsDisbandResult:
        'Permanently tombstone a hosted room id after stopping its work and revoking peer routes.'
        params = _payload({'room_id': room_id, 'cancel_id': cancel_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsDisbandResult', await self._native('groups.disband', params))

    async def list(self, *, include_disbanded: Union[bool, None] | Unset = UNSET, limit: Union[int, None] | Unset = UNSET, offset: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsListResult:
        'List rooms hosted by this gateway, most recently changed first.'
        params = _payload({'include_disbanded': include_disbanded, 'limit': limit, 'offset': offset}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsListResult', await self._native('groups.list', params))

    async def log(self, *, room_id: str, since_seq: Union[int, None] | Unset = UNSET, limit: Union[int, None] | Unset = UNSET, include_disbanded: Union[bool, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsLogResult:
        'A monotonic room-log delta after since_seq, bounded by count and page bytes.'
        params = _payload({'room_id': room_id, 'since_seq': since_seq, 'limit': limit, 'include_disbanded': include_disbanded}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsLogResult', await self._native('groups.log', params))

    async def promote(self, *, room_id: str, confirm: Union[bool, None] | Unset = UNSET, reason: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsPromoteResult:
        'Continue a replicated room on this gateway at epoch + 1; requires confirm=true.'
        params = _payload({'room_id': room_id, 'confirm': confirm, 'reason': reason}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsPromoteResult', await self._native('groups.promote', params))

    async def rename(self, *, room_id: str, event_id: str, name: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsRenameResult:
        'Rename one hosted room atomically with its replay event.'
        params = _payload({'room_id': room_id, 'event_id': event_id, 'name': name}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsRenameResult', await self._native('groups.rename', params))

    async def replica_state(self, *, room_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsReplicaStateResult:
        "The local replica's coverage and authority lineage for one room."
        params = _payload({'room_id': room_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsReplicaStateResult', await self._native('groups.replica_state', params))

    async def replicate(self, *, room_id: str, room_name: str, members: builtins.list[_types_native.RoomMemberInput], page: dict[str, Any], extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsReplicateResult:
        'Persist one authority-stamped replay page into the local replica store; idempotent.'
        params = _payload({'room_id': room_id, 'room_name': room_name, 'members': members, 'page': page}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsReplicateResult', await self._native('groups.replicate', params))

    async def retry(self, *, room_id: str, task_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsRetryResult:
        'Retry one indeterminate room task after explicit user confirmation.'
        params = _payload({'room_id': room_id, 'task_id': task_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsRetryResult', await self._native('groups.retry', params))

    async def send(self, *, room_id: str, event_id: Union[str, None] | Unset = UNSET, payload: dict[str, Any], extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsSendResult:
        'Append one inert message.user event idempotently; the actor is server-owned.'
        params = _payload({'room_id': room_id, 'event_id': event_id, 'payload': payload}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsSendResult', await self._native('groups.send', params))

    async def state(self, *, room_id: str, include_disbanded: Union[bool, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsStateResult:
        "One hosted room's replay cursor and fenced authority state, plus live driver status."
        params = _payload({'room_id': room_id, 'include_disbanded': include_disbanded}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsStateResult', await self._native('groups.state', params))

    async def stop(self, *, room_id: str, cancel_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsStopResult:
        'Durably cancel queued or running work for one hosted room.'
        params = _payload({'room_id': room_id, 'cancel_id': cancel_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsStopResult', await self._native('groups.stop', params))

    @property
    def peer(self) -> NativeGroupsPeerResource:
        return NativeGroupsPeerResource(self._sdk, **self._scope)


class NativeGroupsPeerResource(Resource):
    async def invite(self, *, room_id: Union[str, None] | Unset = UNSET, home_install_id: Union[str, None] | Unset = UNSET, authority_gateway_id: Union[str, None] | Unset = UNSET, authority_epoch: Union[int, None] | Unset = UNSET, member_id: Union[str, None] | Unset = UNSET, grant_id: Union[str, None] | Unset = UNSET, ttl_seconds: Union[float, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsPeerInviteResult:
        'Mint one target-issued room/profile grant for a prospective room home.'
        params = _payload({'room_id': room_id, 'home_install_id': home_install_id, 'authority_gateway_id': authority_gateway_id, 'authority_epoch': authority_epoch, 'member_id': member_id, 'grant_id': grant_id, 'ttl_seconds': ttl_seconds}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsPeerInviteResult', await self._native('groups.peer.invite', params))

    async def register(self, *, room_id: str, member_id: str, target_url: str, target_profile: str, grant: str, catalog: dict[str, Any], cancellation_scope_id: Union[str, None] | Unset = UNSET, trace_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsPeerRegisterResult:
        'Register and probe one scoped peer route on the room home.'
        params = _payload({'room_id': room_id, 'member_id': member_id, 'target_url': target_url, 'target_profile': target_profile, 'grant': grant, 'catalog': catalog, 'cancellation_scope_id': cancellation_scope_id, 'trace_id': trace_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsPeerRegisterResult', await self._native('groups.peer.register', params))

    async def revoke(self, *, grant: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.GroupsPeerRevokeResult:
        'Revoke one target-issued grant using its exact profile scope.'
        params = _payload({'grant': grant}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.GroupsPeerRevokeResult', await self._native('groups.peer.revoke', params))


class NativeHandoffResource(Resource):
    async def fail(self, *, session_id: str, error: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.HandoffFailResult:
        'Fail a not-yet-claimed handoff (client poll timeout); CAS against the watcher.'
        params = _payload({'session_id': session_id, 'error': error}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.HandoffFailResult', await self._native('handoff.fail', params))

    async def request(self, *, session_id: str, platform: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.HandoffRequestResult:
        "Queue a handoff to a messaging platform's home channel; the gateway watcher claims it."
        params = _payload({'session_id': session_id, 'platform': platform}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.HandoffRequestResult', await self._native('handoff.request', params))

    async def state(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.HandoffStateResult:
        'Poll the handoff row for this session.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.HandoffStateResult', await self._native('handoff.state', params))


class NativeImageResource(Resource):
    async def attach(self, *, session_id: str, path: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.AttachedImageResult:
        'Queue a gateway-visible image file for the next turn.'
        params = _payload({'session_id': session_id, 'path': path}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.AttachedImageResult', await self._native('image.attach', params))

    async def attach_bytes(self, *, session_id: str, content_base64: Union[str, None] | Unset = UNSET, data: Union[str, None] | Unset = UNSET, filename: Union[str, None] | Unset = UNSET, ext: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.AttachedImageResult:
        'Queue an image uploaded as base64 (remote client); reply mirrors image.attach.'
        params = _payload({'session_id': session_id, 'content_base64': content_base64, 'data': data, 'filename': filename, 'ext': ext}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.AttachedImageResult', await self._native('image.attach_bytes', params))

    async def detach(self, *, session_id: str, path: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ImageDetachResult:
        'Drop a queued image before the turn is sent.'
        params = _payload({'session_id': session_id, 'path': path}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ImageDetachResult', await self._native('image.detach', params))

    async def generate(self, *, prompt: Union[str, None] | Unset = UNSET, aspect_ratio: Union[str, None] | Unset = UNSET, probe: Union[Any, None] | Unset = UNSET, max_bytes: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ImageGenerateResult:
        "Generate an image through the tool's provider dispatcher and hand the renderer a data URL."
        params = _payload({'prompt': prompt, 'aspect_ratio': aspect_ratio, 'probe': probe, 'max_bytes': max_bytes}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ImageGenerateResult', await self._native('image.generate', params))


class NativeInputResource(Resource):
    async def detect_drop(self, *, session_id: str, text: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.InputDetectDropResult:
        'Recognise a terminal file drop pasted into the composer and turn it into an attachment.'
        params = _payload({'session_id': session_id, 'text': text}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.InputDetectDropResult', await self._native('input.detect_drop', params))


class NativeInsightsResource(Resource):
    async def get(self, *, days: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.InsightsGetResult:
        'Session/message counts over the last ``days`` for the (optionally scoped) profile store.'
        params = _payload({'days': days}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.InsightsGetResult', await self._native('insights.get', params))


class NativeLearningResource(Resource):
    async def delete(self, *, id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.LearningMutationResult:
        'Archive a skill (restorable via curator) or remove a memory chunk.'
        params = _payload({'id': id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.LearningMutationResult', await self._native('learning.delete', params))

    async def detail(self, *, id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.LearningDetailResult:
        'Node content (SKILL.md or memory chunk) for an edit prefill.'
        params = _payload({'id': id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.LearningDetailResult', await self._native('learning.detail', params))

    async def edit(self, *, id: Union[str, None] | Unset = UNSET, content: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.LearningMutationResult:
        "Rewrite a node's content (SKILL.md or memory chunk)."
        params = _payload({'id': id, 'content': content}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.LearningMutationResult', await self._native('learning.edit', params))

    async def frames(self, *, cols: Union[int, None] | Unset = UNSET, rows: Union[int, None] | Unset = UNSET, frames: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.LearningFramesResult:
        'Pre-render the /journey timeline (frames + legend/summary) so the TUI walks it locally.'
        params = _payload({'cols': cols, 'rows': rows, 'frames': frames}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.LearningFramesResult', await self._native('learning.frames', params))


class NativeLlmResource(Resource):
    async def oneshot(self, *, template: Union[str, None] | Unset = UNSET, instructions: Union[str, None] | Unset = UNSET, input: Union[str, None] | Unset = UNSET, variables: Union[dict[str, Any], None] | Unset = UNSET, task: Union[str, None] | Unset = UNSET, temperature: Union[float, None] | Unset = UNSET, max_tokens: Union[int, None] | Unset = UNSET, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.LlmOneshotResult:
        "Stateless one-shot LLM completion (titles, ideas) on the session's or the task backend."
        params = _payload({'template': template, 'instructions': instructions, 'input': input, 'variables': variables, 'task': task, 'temperature': temperature, 'max_tokens': max_tokens, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.LlmOneshotResult', await self._native('llm.oneshot', params))


class NativeMcpResource(Resource):
    async def catalog(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.McpCatalogResult:
        'Curated MCP presets with per-profile installed/enabled state and the env keys each needs.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.McpCatalogResult', await self._native('mcp.catalog', params))

    @property
    def servers(self) -> NativeMcpServersResource:
        return NativeMcpServersResource(self._sdk, **self._scope)


class NativeMcpServersResource(Resource):
    async def add(self, *, name: str, preset: Union[str, None] | Unset = UNSET, config: Union[dict[str, Any], None] | Unset = UNSET, bearer_token: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.McpServersAddResult:
        "Add a server to the profile's config from a catalog preset and/or an explicit config."
        params = _payload({'name': name, 'preset': preset, 'config': config, 'bearer_token': bearer_token}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.McpServersAddResult', await self._native('mcp.servers.add', params))

    async def list(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.McpServersListResult:
        'Configured MCP servers for the (scoped) profile, secrets redacted to env-key names.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.McpServersListResult', await self._native('mcp.servers.list', params))

    async def remove(self, *, name: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.McpServersRemoveResult:
        "Drop a server from the profile's config.yaml."
        params = _payload({'name': name}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.McpServersRemoveResult', await self._native('mcp.servers.remove', params))

    async def set_api_key(self, *, name: str, value: str, env_var: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.McpServersSetApiKeyResult:
        "Store a credential in the profile's .env and reference it from the server config (header or env)."
        params = _payload({'name': name, 'value': value, 'env_var': env_var}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.McpServersSetApiKeyResult', await self._native('mcp.servers.set_api_key', params))

    async def status(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.McpServersStatusResult:
        'Cached runtime state per configured server; never connects, probes, or starts auth.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.McpServersStatusResult', await self._native('mcp.servers.status', params))

    async def test(self, *, name: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.McpServersTestResult:
        'Connect, list tools, disconnect — an OAuth server with no token on disk is reported as not ok.'
        params = _payload({'name': name}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.McpServersTestResult', await self._native('mcp.servers.test', params))

    @property
    def oauth(self) -> NativeMcpServersOauthResource:
        return NativeMcpServersOauthResource(self._sdk, **self._scope)


class NativeMcpServersOauthResource(Resource):
    async def callback(self, *, name: str, session_id: str, code: Union[str, None] | Unset = UNSET, state: Union[str, None] | Unset = UNSET, error: Union[str, None] | Unset = UNSET, iss: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.McpOauthCallbackResult:
        'Relay a client-captured redirect into a client_redirect_uri flow.'
        params = _payload({'name': name, 'session_id': session_id, 'code': code, 'state': state, 'error': error, 'iss': iss}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.McpOauthCallbackResult', await self._native('mcp.servers.oauth.callback', params))

    async def cancel(self, *, name: str, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.McpOauthCancelResult:
        'Cancel a flow owned by the resolved profile, waking its callback worker.'
        params = _payload({'name': name, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.McpOauthCancelResult', await self._native('mcp.servers.oauth.cancel', params))

    async def poll(self, *, name: str, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.McpOauthPollResult:
        'Poll a flow; approved persists tokens for the profile and returns the probed tools.'
        params = _payload({'name': name, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.McpOauthPollResult', await self._native('mcp.servers.oauth.poll', params))

    async def start(self, *, name: str, client_redirect_uri: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.McpOauthStartResult:
        'Begin a PKCE OAuth flow; the client opens auth_url and polls mcp.servers.oauth.poll.'
        params = _payload({'name': name, 'client_redirect_uri': client_redirect_uri}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.McpOauthStartResult', await self._native('mcp.servers.oauth.start', params))


class NativeMessageResource(Resource):
    async def react(self, *, session_id: str, row_id: Union[int, None] | Unset = UNSET, newest_role: Union[str, None] | Unset = UNSET, emoji: Union[str, None] | Unset = UNSET, author: Union[_types_native.ReactionAuthor, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.MessageReactResult:
        "Set/clear one author's emoji reaction on a message; returns the row's full reaction list."
        params = _payload({'session_id': session_id, 'row_id': row_id, 'newest_role': newest_role, 'emoji': emoji, 'author': author}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.MessageReactResult', await self._native('message.react', params))


class NativeModelResource(Resource):
    async def disconnect(self, *, slug: str, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ModelDisconnectResult:
        'Remove every credential (env keys and OAuth state) for a provider.'
        params = _payload({'slug': slug, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ModelDisconnectResult', await self._native('model.disconnect', params))

    async def options(self, *, session_id: Union[str, None] | Unset = UNSET, explicit_only: bool | Unset = UNSET, include_unconfigured: bool | Unset = UNSET, refresh: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ModelOptionsResult:
        "Provider/model inventory for the picker, layered over the session's live provider when given."
        params = _payload({'session_id': session_id, 'explicit_only': explicit_only, 'include_unconfigured': include_unconfigured, 'refresh': refresh}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ModelOptionsResult', await self._native('model.options', params))

    async def save_key(self, *, slug: str, api_key: str, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ModelSaveKeyResult:
        'Save an API key for a provider and return its refreshed inventory row.'
        params = _payload({'slug': slug, 'api_key': api_key, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ModelSaveKeyResult', await self._native('model.save_key', params))


class NativePasteResource(Resource):
    async def collapse(self, *, text: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PasteCollapseResult:
        'Spill a large paste to a file and hand back the inline placeholder.'
        params = _payload({'text': text}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PasteCollapseResult', await self._native('paste.collapse', params))


class NativePdfResource(Resource):
    async def attach(self, *, session_id: str, path: Union[str, None] | Unset = UNSET, content_base64: Union[str, None] | Unset = UNSET, data: Union[str, None] | Unset = UNSET, filename: Union[str, None] | Unset = UNSET, first_page: Union[int, None] | Unset = UNSET, last_page: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PdfAttachResult:
        "Render a PDF's pages to PNG and queue them as images for the next turn."
        params = _payload({'session_id': session_id, 'path': path, 'content_base64': content_base64, 'data': data, 'filename': filename, 'first_page': first_page, 'last_page': last_page}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PdfAttachResult', await self._native('pdf.attach', params))


class NativePetResource(Resource):
    async def cancel(self, *, token: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetCancelResult:
        'Stop an in-flight pet generate/hatch by token (idempotent).'
        params = _payload({'token': token}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetCancelResult', await self._native('pet.cancel', params))

    async def cells(self, *, state: Union[str, None] | Unset = UNSET, cols: Union[int, None] | Unset = UNSET, graphics: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetCellsResult:
        'Half-block cell frames (or a kitty placement) for one pet state.'
        params = _payload({'state': state, 'cols': cols, 'graphics': graphics}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetCellsResult', await self._native('pet.cells', params))

    async def disable(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.OkResult:
        'Turn the pet display off from the desktop picker.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.OkResult', await self._native('pet.disable', params))

    async def export(self, *, slug: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetExportResult:
        'Export an installed pet as a re-importable .zip.'
        params = _payload({'slug': slug}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetExportResult', await self._native('pet.export', params))

    async def gallery(self, *, local_only: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetGalleryResult:
        'Petdex gallery + local install state (installed-only offline); localOnly skips the remote manifest.'
        params = _payload({'localOnly': local_only}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetGalleryResult', await self._native('pet.gallery', params))

    async def generate_call(self, *, prompt: Union[str, None] | Unset = UNSET, reference_image: Union[str, None] | Unset = UNSET, count: Union[int, None] | Unset = UNSET, style: Union[str, None] | Unset = UNSET, provider: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetGenerateResult:
        'Candidate base looks for a new pet (draft step); drafts also stream via pet.generate.progress.'
        params = _payload({'prompt': prompt, 'referenceImage': reference_image, 'count': count, 'style': style, 'provider': provider}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetGenerateResult', await self._native('pet.generate', params))

    async def hatch(self, *, token: str, name: str, cancel_token: Union[str, None] | Unset = UNSET, index: Union[int, None] | Unset = UNSET, description: Union[str, None] | Unset = UNSET, prompt: Union[str, None] | Unset = UNSET, style: Union[str, None] | Unset = UNSET, provider: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetHatchResult:
        'Turn a base draft into a full spritesheet pet; progress streams via pet.hatch.progress.'
        params = _payload({'token': token, 'name': name, 'cancelToken': cancel_token, 'index': index, 'description': description, 'prompt': prompt, 'style': style, 'provider': provider}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetHatchResult', await self._native('pet.hatch', params))

    async def info_call(self, *, known_revision: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetInfoResult:
        'Active pet for sprite renderers: spritesheet (base64) + frame geometry + state-row taxonomy.'
        params = _payload({'knownRevision': known_revision}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetInfoResult', await self._native('pet.info', params))

    async def remove(self, *, slug: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetSlugResult:
        'Uninstall a pet (delete its directory); if it was active, turn the display off.'
        params = _payload({'slug': slug}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetSlugResult', await self._native('pet.remove', params))

    async def rename(self, *, slug: str, name: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetSlugResult:
        "Rename a pet's display name + realign its slug/dir; follows the active slug in config."
        params = _payload({'slug': slug, 'name': name}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetSlugResult', await self._native('pet.rename', params))

    async def scale(self, *, scale: Any | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetScaleResult:
        'Persist display.pet.scale (clamped to engine bounds) from the desktop slider.'
        params = _payload({'scale': scale}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetScaleResult', await self._native('pet.scale', params))

    async def select(self, *, slug: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetSlugResult:
        'Adopt a pet: install (if needed) + activate; writes display.pet.* to config.'
        params = _payload({'slug': slug}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetSlugResult', await self._native('pet.select', params))

    async def thumb(self, *, slug: str, url: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetThumbResult:
        'Idle-frame PNG data URI for the picker (desktop CSP breaks CDN <img>).'
        params = _payload({'slug': slug, 'url': url}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetThumbResult', await self._native('pet.thumb', params))

    @property
    def generate(self) -> NativePetGenerateResource:
        return NativePetGenerateResource(self._sdk, **self._scope)

    @property
    def info(self) -> NativePetInfoResource:
        return NativePetInfoResource(self._sdk, **self._scope)


class NativePetGenerateResource(Resource):
    async def status(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetGenerateStatusResult:
        'Whether pet generation is possible (a reference-capable image backend) and which providers.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetGenerateStatusResult', await self._native('pet.generate.status', params))


class NativePetInfoResource(Resource):
    async def meta(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.PetInfoMetaResult:
        'Cheap active-pet metadata used to avoid full payload refreshes.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PetInfoMetaResult', await self._native('pet.info.meta', params))


class NativePluginsResource(Resource):
    async def list(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.PluginsListResult:
        'Loaded plugin manager entries (legacy flat view); the Plugins Hub uses plugins.manage list.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PluginsListResult', await self._native('plugins.list', params))

    async def manage(self, *, action: _types_native.PluginsAction | Unset = UNSET, key: Union[str, None] | Unset = UNSET, name: Union[str, None] | Unset = UNSET, enable: Union[bool, None] | Unset = UNSET, identifier: Union[str, None] | Unset = UNSET, repo: Union[str, None] | Unset = UNSET, catalog_name: Union[str, None] | Unset = UNSET, force: Union[bool, None] | Unset = UNSET, ref: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PluginsManageResult:
        'Plugins Hub backend: list installed plugins, toggle, git-install, re-pin a catalog install, or remove a user install.'
        params = _payload({'action': action, 'key': key, 'name': name, 'enable': enable, 'identifier': identifier, 'repo': repo, 'catalog_name': catalog_name, 'force': force, 'ref': ref}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PluginsManageResult', await self._native('plugins.manage', params))


class NativePreviewResource(Resource):
    async def restart(self, *, session_id: str, url: str, cwd: Union[str, None] | Unset = UNSET, context: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.TaskIdResult:
        "Spawn a hidden agent that brings the desktop preview's dev server back up."
        params = _payload({'session_id': session_id, 'url': url, 'cwd': cwd, 'context': context}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.TaskIdResult', await self._native('preview.restart', params))


class NativeProcessResource(Resource):
    async def kill(self, *, session_id: str, process_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProcessKillResult:
        "Kill one background process the caller's session owns and return its output snapshot."
        params = _payload({'session_id': session_id, 'process_id': process_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProcessKillResult', await self._native('process.kill', params))

    async def list(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProcessListResult:
        "Background processes owned by the caller's session (desktop status stack poll)."
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProcessListResult', await self._native('process.list', params))

    async def stop(self, *, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProcessStopResult:
        'Kill every background process in the registry (``/stop``), answering the count killed.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProcessStopResult', await self._native('process.stop', params))


class NativeProfilesResource(Resource):
    async def configure(self, *, name: Union[str, None] | Unset = UNSET, ui_meta: Union[dict[str, Any], None] | Unset = UNSET, ui_meta_expected_revisions: Union[dict[str, int], None] | Unset = UNSET, soul: Union[str, None] | Unset = UNSET, description: Union[str, None] | Unset = UNSET, model: Union[str, None] | Unset = UNSET, provider: Union[str, None] | Unset = UNSET, confirm_expensive_model: Union[bool, str, None] | Unset = UNSET, disabled_skills: Union[builtins.list[str], None] | Unset = UNSET, enabled_toolsets: Union[builtins.list[str], None] | Unset = UNSET, enabled_mcp_servers: Union[builtins.list[str], None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProfilesConfigureResult:
        "Editor Save: apply any subset of a profile's sections and report each one."
        params = _payload({'name': name, 'ui_meta': ui_meta, 'ui_meta_expected_revisions': ui_meta_expected_revisions, 'soul': soul, 'description': description, 'model': model, 'provider': provider, 'confirm_expensive_model': confirm_expensive_model, 'disabled_skills': disabled_skills, 'enabled_toolsets': enabled_toolsets, 'enabled_mcp_servers': enabled_mcp_servers}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProfilesConfigureResult', await self._native('profiles.configure', params))

    async def create(self, *, name: str, description: Union[str, None] | Unset = UNSET, clone_from: Union[str, None] | Unset = UNSET, clone_all: Union[bool, str, None] | Unset = UNSET, clone_channels: Union[bool, str, None] | Unset = UNSET, no_skills: Union[bool, str, None] | Unset = UNSET, no_alias: Union[bool, str, None] | Unset = UNSET, soul: Union[str, None] | Unset = UNSET, model: Union[str, None] | Unset = UNSET, provider: Union[str, None] | Unset = UNSET, share_auth: Union[bool, str, None] | Unset = UNSET, mirror_credentials: Union[bool, str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProfilesCreateResult:
        'Create a profile (ws twin of POST /api/profiles), mirroring launch credentials by default.'
        params = _payload({'name': name, 'description': description, 'clone_from': clone_from, 'clone_all': clone_all, 'clone_channels': clone_channels, 'no_skills': no_skills, 'no_alias': no_alias, 'soul': soul, 'model': model, 'provider': provider, 'share_auth': share_auth, 'mirror_credentials': mirror_credentials}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProfilesCreateResult', await self._native('profiles.create', params))

    async def describe(self, *, name: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProfilesDescribeResult:
        'Everything the profile editor shows: soul, model pin, skills, toolsets, MCP servers.'
        params = _payload({'name': name}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProfilesDescribeResult', await self._native('profiles.describe', params))

    async def get_asset(self, *, name: Union[str, None] | Unset = UNSET, asset: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProfilesGetAssetResult:
        'A profile asset as a data URL.'
        params = _payload({'name': name, 'asset': asset}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProfilesGetAssetResult', await self._native('profiles.get_asset', params))

    async def list(self, *, include_sessions: Union[bool, str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProfilesListResult:
        'Roster of profiles with previews so a client paints without N follow-up calls.'
        params = _payload({'include_sessions': include_sessions}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProfilesListResult', await self._native('profiles.list', params))

    async def remember_onboarding(self, *, answers: Union[_types_native.OnboardingAnswers, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProfilesRememberOnboardingResult:
        "Write the onboarding facts into the default profile's user memory and confirm they landed."
        params = _payload({'answers': answers}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProfilesRememberOnboardingResult', await self._native('profiles.remember_onboarding', params))

    async def set_asset(self, *, name: Union[str, None] | Unset = UNSET, asset: Union[str, None] | Unset = UNSET, data: Union[str, None] | Unset = UNSET, clear: Union[bool, str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProfilesSetAssetResult:
        'Store or clear a profile asset (avatar) atomically.'
        params = _payload({'name': name, 'asset': asset, 'data': data, 'clear': clear}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProfilesSetAssetResult', await self._native('profiles.set_asset', params))


class NativeProjectResource(Resource):
    async def facts(self, *, cwd: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectFactsResult:
        "Structured project facts for a cwd so UIs don't re-sniff the workspace."
        params = _payload({'cwd': cwd}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectFactsResult', await self._native('project.facts', params))


class NativeProjectsResource(Resource):
    async def add_folder(self, *, id: str, path: str, label: Union[str, None] | Unset = UNSET, is_primary: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectResult:
        'Attach a folder to a project (optionally as its primary path).'
        params = _payload({'id': id, 'path': path, 'label': label, 'is_primary': is_primary}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectResult', await self._native('projects.add_folder', params))

    async def archive(self, *, id: str, restore: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectsPayload:
        'Archive (or with ``restore`` un-archive) a project; answers the full listing.'
        params = _payload({'id': id, 'restore': restore}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectsPayload', await self._native('projects.archive', params))

    async def create(self, *, name: str, folders: Union[builtins.list[str], None] | Unset = UNSET, slug: Union[str, None] | Unset = UNSET, primary_path: Union[str, None] | Unset = UNSET, description: Union[str, None] | Unset = UNSET, icon: Union[str, None] | Unset = UNSET, color: Union[str, None] | Unset = UNSET, board_slug: Union[str, None] | Unset = UNSET, use: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.OptionalProjectResult:
        'Create a project from a name + folders; duplicate primary paths are refused (5063).'
        params = _payload({'name': name, 'folders': folders, 'slug': slug, 'primary_path': primary_path, 'description': description, 'icon': icon, 'color': color, 'board_slug': board_slug, 'use': use}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.OptionalProjectResult', await self._native('projects.create', params))

    async def delete(self, *, id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectsPayload:
        'Delete a project and its folders; answers the full listing.'
        params = _payload({'id': id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectsPayload', await self._native('projects.delete', params))

    async def discover_repos(self, *, scan: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectsDiscoverReposResult:
        'Repos for the desktop overview: scanned-from-disk (cached) ∪ session-derived.'
        params = _payload({'scan': scan}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectsDiscoverReposResult', await self._native('projects.discover_repos', params))

    async def for_cwd(self, *, cwd: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectsForCwdResult:
        'Which project (if any) owns a directory, plus the resolved cwd and its git branch.'
        params = _payload({'cwd': cwd}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectsForCwdResult', await self._native('projects.for_cwd', params))

    async def get(self, *, id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectResult:
        'One stored project with its folders.'
        params = _payload({'id': id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectResult', await self._native('projects.get', params))

    async def list(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectsPayload:
        'Every project of the profile (archived included) plus which one is active.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectsPayload', await self._native('projects.list', params))

    async def project_sessions(self, *, project_id: str, session_limit: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectsProjectSessionsResult:
        'Fully hydrated lanes for one project, from the same grouping as projects.tree.'
        params = _payload({'project_id': project_id, 'session_limit': session_limit}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectsProjectSessionsResult', await self._native('projects.project_sessions', params))

    async def record_repos(self, *, repos: Union[builtins.list[Union[_types_native.RecordRepoItem, str]], None] | Unset = UNSET, discovery_policy: Union[_types_native.RepoDiscoveryPolicyParams, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectsRecordReposResult:
        "Persist repo roots found by the client's (desktop-side) scan; return the merged list."
        params = _payload({'repos': repos, 'discovery_policy': discovery_policy}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectsRecordReposResult', await self._native('projects.record_repos', params))

    async def remove_folder(self, *, id: str, path: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectResult:
        'Detach a folder from a project.'
        params = _payload({'id': id, 'path': path}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectResult', await self._native('projects.remove_folder', params))

    async def set_active(self, *, id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ActiveIdResult:
        'Switch (or clear) the active project for the profile.'
        params = _payload({'id': id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ActiveIdResult', await self._native('projects.set_active', params))

    async def set_primary(self, *, id: str, path: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectResult:
        "Make one attached folder the project's primary path."
        params = _payload({'id': id, 'path': path}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectResult', await self._native('projects.set_primary', params))

    async def tree(self, *, preview_limit: Union[int, None] | Unset = UNSET, session_limit: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectsTreeResult:
        'Project → repo → lane overview with counts and a few preview sessions per project.'
        params = _payload({'preview_limit': preview_limit, 'session_limit': session_limit}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectsTreeResult', await self._native('projects.tree', params))

    async def update(self, *, id: str, name: Union[str, None] | Unset = UNSET, description: Union[str, None] | Unset = UNSET, icon: Union[str, None] | Unset = UNSET, color: Union[str, None] | Unset = UNSET, board_slug: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ProjectResult:
        "Patch a project's display fields; answers the refreshed project."
        params = _payload({'id': id, 'name': name, 'description': description, 'icon': icon, 'color': color, 'board_slug': board_slug}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ProjectResult', await self._native('projects.update', params))


class NativePromptResource(Resource):
    async def background(self, *, session_id: str, text: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.TaskIdResult:
        'Run a task on a fresh agent in the background; the answer arrives as background.complete.'
        params = _payload({'session_id': session_id, 'text': text}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.TaskIdResult', await self._native('prompt.background', params))

    async def btw(self, *, session_id: str, text: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.TaskIdResult:
        'Side question over a snapshot of the live conversation; the answer arrives as btw.complete.'
        params = _payload({'session_id': session_id, 'text': text}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.TaskIdResult', await self._native('prompt.btw', params))

    async def submit(self, *, session_id: str, text: Any | Unset = UNSET, display_kind: Union[str, None] | Unset = UNSET, interrupted: Union[bool, None] | Unset = UNSET, queued: Union[bool, None] | Unset = UNSET, surface: Union[str, None] | Unset = UNSET, voice_context: Union[str, None] | Unset = UNSET, title_preview: Union[str, None] | Unset = UNSET, truncate_before_user_ordinal: Union[int, None] | Unset = UNSET, truncate_before_row_id: Union[int, None] | Unset = UNSET, truncate_before_message_id: Union[str, None] | Unset = UNSET, confirm_truncate: Union[bool, None] | Unset = UNSET, confirm_empty_truncate: Union[bool, None] | Unset = UNSET, rebind_survivor_row_ids: Union[builtins.list[int], None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.PromptSubmitResult:
        'Send a user turn to a live session; busy sessions queue / steer / redirect instead of refusing.'
        params = _payload({'session_id': session_id, 'text': text, 'display_kind': display_kind, 'interrupted': interrupted, 'queued': queued, 'surface': surface, 'voice_context': voice_context, 'title_preview': title_preview, 'truncate_before_user_ordinal': truncate_before_user_ordinal, 'truncate_before_row_id': truncate_before_row_id, 'truncate_before_message_id': truncate_before_message_id, 'confirm_truncate': confirm_truncate, 'confirm_empty_truncate': confirm_empty_truncate, 'rebind_survivor_row_ids': rebind_survivor_row_ids}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.PromptSubmitResult', await self._native('prompt.submit', params))


class NativeReloadResource(Resource):
    async def env(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.ReloadEnvResult:
        'Re-read ~/.hermes/.env (CLI /reload parity); built agents keep their pool until /new.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ReloadEnvResult', await self._native('reload.env', params))

    async def mcp(self, *, session_id: Union[str, None] | Unset = UNSET, confirm: bool | Unset = UNSET, always: bool | Unset = UNSET, rev: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ReloadMcpResult:
        'Tear down and rediscover MCP servers for every live session (prompt cache is invalidated).'
        params = _payload({'session_id': session_id, 'confirm': confirm, 'always': always, 'rev': rev}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ReloadMcpResult', await self._native('reload.mcp', params))


class NativeRequestResource(Resource):
    async def answer(self, *, id: str, result: dict[str, Any], extra_params: Mapping[str, Any] | None = None) -> _types_native.RequestAnswerResult:
        'Answer an open server→client request from a client that never received the frame.'
        params = _payload({'id': id, 'result': result}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.RequestAnswerResult', await self._native('request.answer', params))


class NativeRollbackResource(Resource):
    async def diff(self, *, session_id: str, hash: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.RollbackDiffResult:
        'Diff between a checkpoint and the working tree, with an ANSI rendering sized to the TUI.'
        params = _payload({'session_id': session_id, 'hash': hash}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.RollbackDiffResult', await self._native('rollback.diff', params))

    async def list(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.RollbackListResult:
        "Checkpoints for the session's cwd; ``enabled: false`` when checkpointing is off."
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.RollbackListResult', await self._native('rollback.list', params))

    async def restore(self, *, session_id: str, hash: str, file_path: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.RollbackRestoreResult:
        'Restore the working tree (or one file) to a checkpoint by hash or 1-based index.'
        params = _payload({'session_id': session_id, 'hash': hash, 'file_path': file_path}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.RollbackRestoreResult', await self._native('rollback.restore', params))


class NativeSessionResource(Resource):
    async def activate(self, *, session_id: str, cols: Union[int, None] | Unset = UNSET, omit_messages: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionActivateResult:
        'Attach the frontend to a live session without closing the previously focused one.'
        params = _payload({'session_id': session_id, 'cols': cols, 'omit_messages': omit_messages}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionActivateResult', await self._native('session.activate', params))

    async def active_list(self, *, current_session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionActiveListResult:
        'Live sessions in this process, insertion order (not a DB browser).'
        params = _payload({'current_session_id': current_session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionActiveListResult', await self._native('session.active_list', params))

    async def branch(self, *, session_id: str, name: Union[str, None] | Unset = UNSET, count: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionBranchResult:
        "Fork a live session into a new stored child that shares the parent's history so far."
        params = _payload({'session_id': session_id, 'name': name, 'count': count}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionBranchResult', await self._native('session.branch', params))

    async def close(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionCloseResult:
        'Tear down a live session (its stored row stays resumable).'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionCloseResult', await self._native('session.close', params))

    async def compress(self, *, session_id: str, focus_topic: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionCompressResult:
        'Manual /compress of an idle session, optionally focused on a topic.'
        params = _payload({'session_id': session_id, 'focus_topic': focus_topic}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionCompressResult', await self._native('session.compress', params))

    async def context_breakdown(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionContextBreakdownResult:
        'Cursor-style split of the context window by category.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionContextBreakdownResult', await self._native('session.context_breakdown', params))

    async def control_call(self, *, session_id: str, action: str, args: Union[_types_native.SessionControlArgs, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionControlResult:
        'Run one allowlisted goal / loop / subgoal / heartbeat action and return the exact resulting snapshot.'
        params = _payload({'session_id': session_id, 'action': action, 'args': args}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionControlResult', await self._native('session.control', params))

    async def create(self, *, cols: Union[int, None] | Unset = UNSET, source: Union[str, None] | Unset = UNSET, cwd: Union[str, None] | Unset = UNSET, messages: Union[builtins.list[_types_native.SeedMessage], None] | Unset = UNSET, parent_session_id: Union[str, None] | Unset = UNSET, title: Union[str, None] | Unset = UNSET, model: Union[str, None] | Unset = UNSET, provider: Union[str, None] | Unset = UNSET, reasoning_effort: Union[str, None] | Unset = UNSET, fast: Union[bool, None] | Unset = UNSET, close_on_disconnect: bool | Unset = UNSET, hidden: bool | Unset = UNSET, room_plumbing: bool | Unset = UNSET, follow_profile_config: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionCreateResult:
        'Mint a live session (agent builds after the reply); a DB row appears on the first prompt unless seeded.'
        params = _payload({'cols': cols, 'source': source, 'cwd': cwd, 'messages': messages, 'parent_session_id': parent_session_id, 'title': title, 'model': model, 'provider': provider, 'reasoning_effort': reasoning_effort, 'fast': fast, 'close_on_disconnect': close_on_disconnect, 'hidden': hidden, 'room_plumbing': room_plumbing, 'follow_profile_config': follow_profile_config}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionCreateResult', await self._native('session.create', params))

    async def delete(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionDeleteResult:
        'Delete a stored session + transcripts; refused while it is live here.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionDeleteResult', await self._native('session.delete', params))

    async def history(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionHistoryResult:
        'The durable display transcript (ancestors included, row ids attached).'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionHistoryResult', await self._native('session.history', params))

    async def interrupt(self, *, session_id: str, expected_hosted_task_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionInterruptResult:
        'Stop the running turn (and streaming TTS); retires the crash-recovery marker.'
        params = _payload({'session_id': session_id, 'expected_hosted_task_id': expected_hosted_task_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionInterruptResult', await self._native('session.interrupt', params))

    async def list(self, *, title: Union[str, None] | Unset = UNSET, limit: Union[int, None] | Unset = UNSET, include_hidden: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionListResult:
        'Human-facing stored sessions, most recent first (sub-agent / kanban sources denied).'
        params = _payload({'title': title, 'limit': limit, 'include_hidden': include_hidden}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionListResult', await self._native('session.list', params))

    async def most_recent(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionMostRecentResult:
        'Most recent human-facing session; errors fold into a null session_id.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionMostRecentResult', await self._native('session.most_recent', params))

    async def redirect(self, *, session_id: str, text: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionCorrectionResult:
        'Redirect the active turn (queued for the next turn while the agent is still building).'
        params = _payload({'session_id': session_id, 'text': text}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionCorrectionResult', await self._native('session.redirect', params))

    async def resume(self, *, session_id: str, cols: Union[int, None] | Unset = UNSET, source: Union[str, None] | Unset = UNSET, lazy: bool | Unset = UNSET, defer_history: bool | Unset = UNSET, omit_messages: bool | Unset = UNSET, eager_build: bool | Unset = UNSET, close_on_disconnect: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionResumeResult:
        'Attach to a stored session: reuse it if live here, else lazy / deferred / cold / eager rebuild.'
        params = _payload({'session_id': session_id, 'cols': cols, 'source': source, 'lazy': lazy, 'defer_history': defer_history, 'omit_messages': omit_messages, 'eager_build': eager_build, 'close_on_disconnect': close_on_disconnect}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionResumeResult', await self._native('session.resume', params))

    async def save(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionSaveResult:
        'Export the transcript to ~/.hermes/sessions/saved (classic /save).'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionSaveResult', await self._native('session.save', params))

    async def set_hidden(self, *, session_id: str, hidden: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionSetHiddenResult:
        'Set/clear hidden (out of the default list, still resumable by its owner) on a session + lineage.'
        params = _payload({'session_id': session_id, 'hidden': hidden}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionSetHiddenResult', await self._native('session.set_hidden', params))

    async def status(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionStatusResult:
        'Rendered /status text for the session.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionStatusResult', await self._native('session.status', params))

    async def steer(self, *, session_id: str, text: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionCorrectionResult:
        'Inject text into the next tool result without interrupting the turn.'
        params = _payload({'session_id': session_id, 'text': text}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionCorrectionResult', await self._native('session.steer', params))

    async def title(self, *, session_id: str, title: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionTitleResult:
        "Read or set a live session's title; a title set before the row exists is queued."
        params = _payload({'session_id': session_id, 'title': title}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionTitleResult', await self._native('session.title', params))

    async def undo(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionUndoResult:
        'Drop the last user turn (and everything after it) from an idle session.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionUndoResult', await self._native('session.undo', params))

    async def usage(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionUsageResult:
        'Token / context / cost counters for the session (+ Nous credit lines when available).'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionUsageResult', await self._native('session.usage', params))

    @property
    def control(self) -> NativeSessionControlResource:
        return NativeSessionControlResource(self._sdk, **self._scope)

    @property
    def cwd(self) -> NativeSessionCwdResource:
        return NativeSessionCwdResource(self._sdk, **self._scope)

    @property
    def events(self) -> NativeSessionEventsResource:
        return NativeSessionEventsResource(self._sdk, **self._scope)

    @property
    def foreign(self) -> NativeSessionForeignResource:
        return NativeSessionForeignResource(self._sdk, **self._scope)

    @property
    def workspace(self) -> NativeSessionWorkspaceResource:
        return NativeSessionWorkspaceResource(self._sdk, **self._scope)


class NativeSessionControlResource(Resource):
    async def read(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionControlReadResult:
        "Stable, allowlisted snapshot of one live session's goal / loop / heartbeat state."
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionControlReadResult', await self._native('session.control.read', params))


class NativeSessionCwdResource(Resource):
    async def set(self, *, session_id: str, cwd: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionCwdSetResult:
        "Change a live, idle session's working directory."
        params = _payload({'session_id': session_id, 'cwd': cwd}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionCwdSetResult', await self._native('session.cwd.set', params))


class NativeSessionEventsResource(Resource):
    async def since(self, *, session_id: str, last_seen: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionEventsSinceResult:
        'Replay events after a seq watermark on WS reconnect; truncated means refetch state.'
        params = _payload({'session_id': session_id, 'last_seen': last_seen}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionEventsSinceResult', await self._native('session.events.since', params))

    async def stats(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionEventsStatsResult:
        'Replay-buffer occupancy telemetry (ops/debug).'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionEventsStatsResult', await self._native('session.events.stats', params))


class NativeSessionForeignResource(Resource):
    async def method_import(self, *, id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionForeignImportResult:
        "Import a foreign session into this profile's history (idempotent per origin)."
        params = _payload({'id': id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionForeignImportResult', await self._native('session.foreign.import', params))

    async def list(self, *, source: Union[_types_native.ForeignSource, None] | Unset = UNSET, offset: Union[int, None] | Unset = UNSET, limit: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionForeignListResult:
        'One page of Claude Code / Codex sessions found on the serving backend.'
        params = _payload({'source': source, 'offset': offset, 'limit': limit}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionForeignListResult', await self._native('session.foreign.list', params))

    async def preview(self, *, id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionForeignPreviewResult:
        "Preview a foreign session's tail before importing it."
        params = _payload({'id': id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionForeignPreviewResult', await self._native('session.foreign.preview', params))


class NativeSessionWorkspaceResource(Resource):
    async def move(self, *, session_key: str, cwd: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SessionWorkspaceMoveResult:
        "Re-home a stored session's workspace; git identity is replaced and a live agent follows."
        params = _payload({'session_key': session_key, 'cwd': cwd}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SessionWorkspaceMoveResult', await self._native('session.workspace.move', params))


class NativeSetupResource(Resource):
    async def runtime_check(self, *, provider: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SetupRuntimeCheckResult:
        'Strict provider check through the same runtime resolution the agent uses on session creation.'
        params = _payload({'provider': provider}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SetupRuntimeCheckResult', await self._native('setup.runtime_check', params))

    async def status(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.SetupStatusResult:
        'Loose provider check: is ANY provider auth state discoverable for the (launch or named) profile.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SetupStatusResult', await self._native('setup.status', params))


class NativeShellResource(Resource):
    async def exec(self, *, command: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.ShellExecResult:
        'Run a safe (non-dangerous) shell command captured for ``!cmd`` / inline substitution.'
        params = _payload({'command': command}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ShellExecResult', await self._native('shell.exec', params))


class NativeSkillsResource(Resource):
    async def manage(self, *, action: _types_native.SkillsAction | Unset = UNSET, query: Union[str, None] | Unset = UNSET, page: Union[int, None] | Unset = UNSET, page_size: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SkillsManageResult:
        "Skills hub backend: list the profile's skills or search / browse / inspect / install from the hub."
        params = _payload({'action': action, 'query': query, 'page': page, 'page_size': page_size}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SkillsManageResult', await self._native('skills.manage', params))

    async def reload(self, *, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SkillsReloadResult:
        'Re-scan skill dirs; the pre-rendered ``output`` is what /reload-skills prints.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SkillsReloadResult', await self._native('skills.reload', params))


class NativeSlashResource(Resource):
    async def exec(self, *, session_id: str, command: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SlashExecResult:
        "Execute a slash command against the session's slash worker (or a live/plugin shortcut)."
        params = _payload({'session_id': session_id, 'command': command}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SlashExecResult', await self._native('slash.exec', params))


class NativeSpawnTreeResource(Resource):
    async def list(self, *, session_id: Union[str, None] | Unset = UNSET, cross_session: bool | Unset = UNSET, limit: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SpawnTreeListResult:
        'Saved spawn-tree snapshots, newest first.'
        params = _payload({'session_id': session_id, 'cross_session': cross_session, 'limit': limit}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SpawnTreeListResult', await self._native('spawn_tree.list', params))

    async def load(self, *, path: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SpawnTreeLoadResult:
        'Read one saved spawn-tree snapshot (path must be under the spawn-trees root).'
        params = _payload({'path': path}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SpawnTreeLoadResult', await self._native('spawn_tree.load', params))

    async def save(self, *, subagents: builtins.list[dict[str, Any]], session_id: Union[str, None] | Unset = UNSET, started_at: Union[float, None] | Unset = UNSET, finished_at: Union[float, None] | Unset = UNSET, label: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SpawnTreeSaveResult:
        "Persist a finished delegation tree snapshot under the session's spawn-trees dir."
        params = _payload({'subagents': subagents, 'session_id': session_id, 'started_at': started_at, 'finished_at': finished_at, 'label': label}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SpawnTreeSaveResult', await self._native('spawn_tree.save', params))


class NativeSubagentResource(Resource):
    async def interrupt(self, *, session_id: str, subagent_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SubagentInterruptResult:
        'Hard-interrupt one owned child; ``found`` is false when it already finished.'
        params = _payload({'session_id': session_id, 'subagent_id': subagent_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SubagentInterruptResult', await self._native('subagent.interrupt', params))

    async def list(self, *, session_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SubagentListResult:
        "Live children owned by this session (other sessions' children never leak)."
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SubagentListResult', await self._native('subagent.list', params))

    async def steer(self, *, session_id: str, subagent_id: str, text: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SubagentSteerResult:
        'Queue steering text into a live delegated child owned by this session.'
        params = _payload({'session_id': session_id, 'subagent_id': subagent_id, 'text': text}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SubagentSteerResult', await self._native('subagent.steer', params))

    async def tail(self, *, session_id: str, subagent_id: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.SubagentTailResult:
        "Last 16KB of an owned child's live transcript."
        params = _payload({'session_id': session_id, 'subagent_id': subagent_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SubagentTailResult', await self._native('subagent.tail', params))


class NativeSubscriptionResource(Resource):
    async def change(self, *, subscription_type_id: Union[str, None] | Unset = UNSET, cancel: bool | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.BillingPendingChangeResult:
        'Schedule a downgrade / same-price change or a period-end cancellation.'
        params = _payload({'subscription_type_id': subscription_type_id, 'cancel': cancel}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BillingPendingChangeResult', await self._native('subscription.change', params))

    async def preview(self, *, subscription_type_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SubscriptionPreviewResult:
        'Chargeless quote of what a plan change would do (billing:manage).'
        params = _payload({'subscription_type_id': subscription_type_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SubscriptionPreviewResult', await self._native('subscription.preview', params))

    async def resume(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.BillingPendingChangeResult:
        'Clear a scheduled downgrade / cancellation (re-enables recurring spend).'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.BillingPendingChangeResult', await self._native('subscription.resume', params))

    async def state(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.SubscriptionStateResult:
        'Current plan, tier catalog and usage for the picker; fail-open when logged out.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SubscriptionStateResult', await self._native('subscription.state', params))

    async def upgrade(self, *, subscription_type_id: Union[str, None] | Unset = UNSET, idempotency_key: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.SubscriptionUpgradeResult:
        'Prorate, charge and flip the plan (billing:manage, idempotent).'
        params = _payload({'subscription_type_id': subscription_type_id, 'idempotency_key': idempotency_key}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SubscriptionUpgradeResult', await self._native('subscription.upgrade', params))


class NativeSystemResource(Resource):
    async def battery(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.SystemBatteryResult:
        'Host battery for the status bar; always resolves, ``available: false`` when unreadable.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.SystemBatteryResult', await self._native('system.battery', params))


class NativeTerminalResource(Resource):
    async def resize(self, *, session_id: str, cols: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.TerminalResizeResult:
        "Record the client's column width for server-side rendering."
        params = _payload({'session_id': session_id, 'cols': cols}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.TerminalResizeResult', await self._native('terminal.resize', params))


class NativeToolsResource(Resource):
    async def configure(self, *, action: _types_native.ToolsAction, names: builtins.list[str], session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ToolsConfigureResult:
        'Persist a toolset / MCP enable-disable change and rebuild the session agent so it takes effect now.'
        params = _payload({'action': action, 'names': names, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ToolsConfigureResult', await self._native('tools.configure', params))

    async def list(self, *, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ToolsetsListResult:
        "Every toolset with its resolved tool names, flagged against the session's (or config's) enabled set."
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ToolsetsListResult', await self._native('tools.list', params))

    async def show(self, *, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ToolsShowResult:
        'The /tools listing grouped by toolset, including tools deferred behind the tool_search bridge.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ToolsShowResult', await self._native('tools.show', params))


class NativeToolsetsResource(Resource):
    async def list(self, *, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.ToolsetsListResult:
        'Toolset summaries (no tool names) for the desktop Toolsets tab.'
        params = _payload({'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.ToolsetsListResult', await self._native('toolsets.list', params))


class NativeUsageResource(Resource):
    async def bars(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.UsageModel:
        'Two-bar dollar usage view shared by /usage, /topup and /subscription; fail-open to unavailable.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.UsageModel', await self._native('usage.bars', params))


class NativeVaultResource(Resource):
    async def add(self, *, kind: Union[_types_native.VaultKind, None] | Unset = UNSET, label: Union[str, None] | Unset = UNSET, origin: Union[str, None] | Unset = UNSET, secret: Union[dict[str, Any], None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.VaultAddResult:
        'Add a login / payment / address item to the local vault.'
        params = _payload({'kind': kind, 'label': label, 'origin': origin, 'secret': secret}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.VaultAddResult', await self._native('vault.add', params))

    async def list(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.VaultListResult:
        'Metadata-only listing across the local vault and every unlocked password manager.'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.VaultListResult', await self._native('vault.list', params))

    async def lock(self, *, name: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.VaultLockResult:
        "Forget a manager's session token (every manager when no name is given)."
        params = _payload({'name': name}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.VaultLockResult', await self._native('vault.lock', params))

    async def remove(self, *, id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.VaultRemoveResult:
        'Remove a local vault item by id.'
        params = _payload({'id': id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.VaultRemoveResult', await self._native('vault.remove', params))

    async def sources(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.VaultSourcesResult:
        'Status of every login source (local vault + detected password managers).'
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.VaultSourcesResult', await self._native('vault.sources', params))

    async def unlock(self, *, name: Union[str, None] | Unset = UNSET, password: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.VaultUnlockResult:
        'Unlock a password manager for this session with its master password.'
        params = _payload({'name': name, 'password': password}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.VaultUnlockResult', await self._native('vault.unlock', params))

    @property
    def source(self) -> NativeVaultSourceResource:
        return NativeVaultSourceResource(self._sdk, **self._scope)


class NativeVaultSourceResource(Resource):
    async def set(self, *, name: Union[str, None] | Unset = UNSET, enabled: Union[bool, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.VaultSourceSetResult:
        'Enable or disable an external password manager (disabling also locks it).'
        params = _payload({'name': name, 'enabled': enabled}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.VaultSourceSetResult', await self._native('vault.source.set', params))


class NativeVerificationResource(Resource):
    async def status(self, *, session_id: Union[str, None] | Unset = UNSET, session_key: Union[str, None] | Unset = UNSET, cwd: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.VerificationStatusResult:
        'Best known verification evidence for a cwd/session; read-only, never runs checks.'
        params = _payload({'session_id': session_id, 'session_key': session_key, 'cwd': cwd}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.VerificationStatusResult', await self._native('verification.status', params))


class NativeVoiceResource(Resource):
    async def record(self, *, action: _types_native.VoiceRecordAction | Unset = UNSET, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.VoiceRecordResult:
        'VAD-bounded push-to-talk; the transcript arrives as a voice.transcript event.'
        params = _payload({'action': action, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.VoiceRecordResult', await self._native('voice.record', params))

    async def toggle(self, *, action: _types_native.VoiceToggleAction | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.VoiceToggleResult:
        '/voice parity: report, flip voice mode on/off, or toggle speech output.'
        params = _payload({'action': action}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.VoiceToggleResult', await self._native('voice.toggle', params))

    async def tts(self, *, text: str, extra_params: Mapping[str, Any] | None = None) -> _types_native.VoiceTtsResult:
        'Speak text through the backend TTS engine (barge-in aware).'
        params = _payload({'text': text}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.VoiceTtsResult', await self._native('voice.tts', params))


class NativeWakeResource(Resource):
    async def feed(self, *, pcm: Union[str, None] | Unset = UNSET, pcm_b64: Union[str, None] | Unset = UNSET, sample_rate: Union[int, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.WakeFeedResult:
        'Push client-captured PCM into the armed detector (mic-less remote backends).'
        params = _payload({'pcm': pcm, 'pcm_b64': pcm_b64, 'sample_rate': sample_rate}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.WakeFeedResult', await self._native('wake.feed', params))

    async def pause(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.WakePauseResult:
        "Release the mic (e.g. while the desktop's browser captures audio)."
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.WakePauseResult', await self._native('wake.pause', params))

    async def resume(self, *, extra_params: Mapping[str, Any] | None = None) -> _types_native.WakeResumeResult:
        "Reclaim the mic after a pause; no-op if the listener isn't armed."
        params = _payload({}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.WakeResumeResult', await self._native('wake.resume', params))

    async def start(self, *, surface: Union[str, None] | Unset = UNSET, persist: Union[bool, None] | Unset = UNSET, client_capture: Union[bool, None] | Unset = UNSET, session_id: Union[str, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.WakeStartResult:
        'Arm the wake-word listener for the calling surface; refusals explain why.'
        params = _payload({'surface': surface, 'persist': persist, 'client_capture': client_capture, 'session_id': session_id}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.WakeStartResult', await self._native('wake.start', params))

    async def status(self, *, surface: Union[str, None] | Unset = UNSET, client_capture: Union[bool, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.WakeStatusResult:
        'Everything a client needs to draw the wake-word state and decide whether to (re)arm.'
        params = _payload({'surface': surface, 'client_capture': client_capture}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.WakeStatusResult', await self._native('wake.status', params))

    async def stop(self, *, persist: Union[bool, None] | Unset = UNSET, extra_params: Mapping[str, Any] | None = None) -> _types_native.WakeStopResult:
        "Stop this surface's listener; persist also writes wake_word.enabled: false."
        params = _payload({'persist': persist}, extra_params)
        if 'profile' in params:
            raise TypeError('Profile is bound by the resource; select another profile resource')
        return typing.cast('_types_native.WakeStopResult', await self._native('wake.stop', params))


class PoolResource(Resource):
    async def get(self) -> _types_control_plane.InstancePool:
        return typing.cast('_types_control_plane.InstancePool', await self._invoke('getPool', _payload({})))

    async def update(self, *, minimum_size: int | Unset = UNSET, maximum_size: int | Unset = UNSET, desired_size: int | Unset = UNSET, strategy: _types_control_plane.SchedulingStrategy | Unset = UNSET, idle_ttl_seconds: int | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_control_plane.InstancePool:
        body = _payload({'minimumSize': minimum_size, 'maximumSize': maximum_size, 'desiredSize': desired_size, 'strategy': strategy, 'idleTtlSeconds': idle_ttl_seconds}, extra_body)
        return typing.cast('_types_control_plane.InstancePool', await self._invoke('updatePool', _payload({'body': body})))

    async def delete(self) -> Any:
        return await self._invoke('deletePool', _payload({}))

    @property
    def leases(self) -> LeasesResource:
        return LeasesResource(self._sdk, **self._scope)


class PoolsResource(Resource):
    async def list(self) -> _types_control_plane.listPoolsResult:
        return typing.cast('_types_control_plane.listPoolsResult', await self._invoke('listPools', _payload({})))

    async def create(self, *, name: str, template: _types_control_plane.InstanceTemplate, minimum_size: int | Unset = UNSET, maximum_size: int | Unset = UNSET, desired_size: int | Unset = UNSET, strategy: _types_control_plane.SchedulingStrategy | Unset = UNSET, idle_ttl_seconds: int | Unset = UNSET, kubernetes: _types_control_plane.KubernetesPoolSpec | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_control_plane.InstancePool:
        body = _payload({'name': name, 'template': template, 'minimumSize': minimum_size, 'maximumSize': maximum_size, 'desiredSize': desired_size, 'strategy': strategy, 'idleTtlSeconds': idle_ttl_seconds, 'kubernetes': kubernetes}, extra_body)
        return typing.cast('_types_control_plane.InstancePool', await self._invoke('createPool', _payload({'body': body})))

    def __call__(self, pool_id: str) -> PoolResource:
        if not pool_id:
            raise ValueError('Resource ID must not be empty')
        return PoolResource(self._sdk, **{**self._scope, 'pool_id': pool_id})


class ProfileResource(Resource):
    async def get(self) -> _types_control_plane.Profile:
        return typing.cast('_types_control_plane.Profile', await self._invoke('getProfile', _payload({})))

    async def update(self, *, description: str | Unset = UNSET, soul: str | Unset = UNSET, model: str | Unset = UNSET, provider: str | Unset = UNSET, config: dict[str, Any] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_control_plane.Profile:
        body = _payload({'description': description, 'soul': soul, 'model': model, 'provider': provider, 'config': config}, extra_body)
        return typing.cast('_types_control_plane.Profile', await self._invoke('updateProfile', _payload({'body': body})))

    async def delete(self) -> Any:
        return await self._invoke('deleteProfile', _payload({}))

    async def request(self, *, jsonrpc: Literal['2.0'], id: Union[str, int, None] | Unset = UNSET, method: str, params: Union[dict[str, Any], builtins.list[Any]] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_runtime.JsonRpcResponse:
        body = _payload({'jsonrpc': jsonrpc, 'id': id, 'method': method, 'params': params}, extra_body)
        return typing.cast('_types_runtime.JsonRpcResponse', await self._invoke('invokeHermesRpc', _payload({'body': body})))

    @property
    def sessions(self) -> SessionsResource:
        return SessionsResource(self._sdk, **self._scope)

    @property
    def native(self) -> NativeResource:
        return NativeResource(self._sdk, **self._scope)

    def connect(self) -> AbstractAsyncContextManager[NativeConnection]:
        return connect(self._sdk, instance_id=self._scope['instance_id'], profile_id=self._scope['profile_id'])


class ProfilesResource(Resource):
    async def list(self) -> _types_control_plane.listProfilesResult:
        return typing.cast('_types_control_plane.listProfilesResult', await self._invoke('listProfiles', _payload({})))

    async def create(self, *, name: str, description: str | Unset = UNSET, clone_from: str | Unset = UNSET, clone_all: bool | Unset = UNSET, clone_channels: bool | Unset = UNSET, include_skills: bool | Unset = UNSET, soul: str | Unset = UNSET, model: str | Unset = UNSET, provider: str | Unset = UNSET, mirror_credentials: bool | Unset = UNSET, config: dict[str, Any] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_control_plane.Profile:
        body = _payload({'name': name, 'description': description, 'cloneFrom': clone_from, 'cloneAll': clone_all, 'cloneChannels': clone_channels, 'includeSkills': include_skills, 'soul': soul, 'model': model, 'provider': provider, 'mirrorCredentials': mirror_credentials, 'config': config}, extra_body)
        return typing.cast('_types_control_plane.Profile', await self._invoke('createProfile', _payload({'body': body})))

    def __call__(self, profile_id: str) -> ProfileResource:
        if not profile_id:
            raise ValueError('Resource ID must not be empty')
        return ProfileResource(self._sdk, **{**self._scope, 'profile_id': profile_id})


class RecipeResource(Resource):
    async def get(self) -> _types_images.ImageRecipe:
        return typing.cast('_types_images.ImageRecipe', await self._invoke('getImageRecipe', _payload({})))

    async def delete(self) -> Any:
        return await self._invoke('deleteImageRecipe', _payload({}))


class RecipesResource(Resource):
    async def list(self, *, owner_id: str | Unset = UNSET) -> _types_images.ImageRecipePage:
        return typing.cast('_types_images.ImageRecipePage', await self._invoke('listImageRecipes', _payload({'owner_id': owner_id})))

    async def create(self, *, idempotency_key: str | Unset = UNSET, owner: _types_images.OwnerReference, name: str, base_image: str, platforms: builtins.list[Literal['linux/amd64', 'linux/arm64']] | Unset = UNSET, packages: _types_images.PackageSpec | Unset = UNSET, artifacts: builtins.list[_types_images.ArtifactMount] | Unset = UNSET, labels: dict[str, str] | Unset = UNSET, build_arguments: dict[str, str] | Unset = UNSET, runtime: _types_images.createImageRecipeRuntime | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_images.ImageRecipe:
        body = _payload({'owner': owner, 'name': name, 'baseImage': base_image, 'platforms': platforms, 'packages': packages, 'artifacts': artifacts, 'labels': labels, 'buildArguments': build_arguments, 'runtime': runtime}, extra_body)
        return typing.cast('_types_images.ImageRecipe', await self._invoke('createImageRecipe', _payload({'idempotency_key': idempotency_key, 'body': body})))

    def __call__(self, recipe_id: str) -> RecipeResource:
        if not recipe_id:
            raise ValueError('Resource ID must not be empty')
        return RecipeResource(self._sdk, **{**self._scope, 'recipe_id': recipe_id})


class RootResource(Resource):
    async def capabilities(self) -> _types_control_plane.ControlPlaneCapabilities:
        return typing.cast('_types_control_plane.ControlPlaneCapabilities', await self._invoke('getControlPlaneCapabilities', _payload({})))

    @property
    def instances(self) -> InstancesResource:
        return InstancesResource(self._sdk, **self._scope)

    @property
    def pools(self) -> PoolsResource:
        return PoolsResource(self._sdk, **self._scope)

    @property
    def jobs(self) -> JobsResource:
        return JobsResource(self._sdk, **self._scope)

    @property
    def images(self) -> ImagesResource:
        return ImagesResource(self._sdk, **self._scope)

    @property
    def tools(self) -> ToolsResource:
        return ToolsResource(self._sdk, **self._scope)

    @property
    def inference(self) -> InferenceResource:
        return InferenceResource(self._sdk, **self._scope)


class SessionResource(Resource):
    async def get(self) -> _types_runtime.Session:
        return typing.cast('_types_runtime.Session', await self._invoke('getSession', _payload({})))

    async def delete(self) -> Any:
        return await self._invoke('deleteSession', _payload({}))

    async def action(self, *, body: _types_runtime.SessionAction) -> _types_runtime.Session:
        return typing.cast('_types_runtime.Session', await self._invoke('actOnSession', _payload({'body': body})))

    def events(self, *, after: str | Unset = UNSET) -> AsyncIterator[dict[str, Any]]:
        return self._stream('streamSessionEvents', _payload({'after': after}))

    @property
    def turns(self) -> TurnsResource:
        return TurnsResource(self._sdk, **self._scope)


class SessionsResource(Resource):
    async def list(self, *, cursor: str | Unset = UNSET) -> _types_runtime.SessionPage:
        return typing.cast('_types_runtime.SessionPage', await self._invoke('listSessions', _payload({'cursor': cursor})))

    async def create(self, *, idempotency_key: str | Unset = UNSET, title: str | Unset = UNSET, resume_native_session_id: str | Unset = UNSET, working_directory: str | Unset = UNSET, environment: dict[str, str] | Unset = UNSET, metadata: dict[str, Any] | Unset = UNSET, tool_binding_ids: builtins.list[str] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_runtime.Session:
        body = _payload({'title': title, 'resumeNativeSessionId': resume_native_session_id, 'workingDirectory': working_directory, 'environment': environment, 'metadata': metadata, 'toolBindingIds': tool_binding_ids}, extra_body)
        return typing.cast('_types_runtime.Session', await self._invoke('createSession', _payload({'idempotency_key': idempotency_key, 'body': body})))

    def __call__(self, session_id: str) -> SessionResource:
        if not session_id:
            raise ValueError('Resource ID must not be empty')
        return SessionResource(self._sdk, **{**self._scope, 'session_id': session_id})


class ToolsResource(Resource):
    async def call(self, *, call_id: str, tool: str, arguments: dict[str, Any], target: _types_tools.BindingScope, deadline: str | Unset = UNSET, metadata: dict[str, Any] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_tools.ToolCallResult:
        body = _payload({'callId': call_id, 'tool': tool, 'arguments': arguments, 'target': target, 'deadline': deadline, 'metadata': metadata}, extra_body)
        return typing.cast('_types_tools.ToolCallResult', await self._invoke('executeToolCall', _payload({'body': body})))

    @property
    def bundles(self) -> BundlesResource:
        return BundlesResource(self._sdk, **self._scope)

    @property
    def bindings(self) -> BindingsResource:
        return BindingsResource(self._sdk, **self._scope)

    @property
    def mcp_servers(self) -> McpServersResource:
        return McpServersResource(self._sdk, **self._scope)


class TurnResource(Resource):
    async def get(self) -> _types_runtime.Turn:
        return typing.cast('_types_runtime.Turn', await self._invoke('getTurn', _payload({})))

    async def action(self, *, body: _types_runtime.TurnAction) -> Any:
        return await self._invoke('actOnTurn', _payload({'body': body}))

    async def wait(self, *, timeout: float = 300, poll_interval: float = 0.5) -> _types_runtime.Turn:
        return typing.cast('_types_runtime.Turn', await self._wait('getTurn', 'status', set(['completed', 'failed', 'stopped', 'waiting_for_approval']), timeout=timeout, poll_interval=poll_interval))

    async def stop(self) -> Any:
        return await self.action(body={'type': 'stop'})

    async def steer(self, content: str) -> Any:
        return await self.action(body={'type': 'steer', 'content': content})

    async def approve(self, request_id: str, decision: Literal['allow_once', 'allow_session', 'deny']) -> Any:
        return await self.action(body={'type': 'approval', 'requestId': request_id, 'decision': decision})


class TurnsResource(Resource):
    async def submit(self, *, idempotency_key: str | Unset = UNSET, content: Union[str, builtins.list[_types_runtime.ContentPart]], mode: Literal['enqueue', 'steer'] | Unset = UNSET, tool_binding_ids: builtins.list[str] | Unset = UNSET, metadata: dict[str, Any] | Unset = UNSET, extra_body: Mapping[str, Any] | None = None) -> _types_runtime.Turn:
        body = _payload({'content': content, 'mode': mode, 'toolBindingIds': tool_binding_ids, 'metadata': metadata}, extra_body)
        return typing.cast('_types_runtime.Turn', await self._invoke('submitTurn', _payload({'idempotency_key': idempotency_key, 'body': body})))

    def __call__(self, turn_id: str) -> TurnResource:
        if not turn_id:
            raise ValueError('Resource ID must not be empty')
        return TurnResource(self._sdk, **{**self._scope, 'turn_id': turn_id})
