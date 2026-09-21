"""Generated namespace clients. Do not edit."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Any

from ..transport import AsyncTransport
from .operations import BY_ID, HERMES_RPC_METHODS


class _AsyncAPI:
    def __init__(self, transport: AsyncTransport):
        self._transport = transport


class AsyncControlPlaneAPI(_AsyncAPI):
    async def list_instances(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['listInstances'], arguments)

    async def create_instance(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['createInstance'], arguments)

    async def get_instance(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getInstance'], arguments)

    async def update_instance(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['updateInstance'], arguments)

    async def delete_instance(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['deleteInstance'], arguments)

    async def change_instance_state(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['changeInstanceState'], arguments)

    async def get_instance_connection(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getInstanceConnection'], arguments)

    async def get_instance_capabilities(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getInstanceCapabilities'], arguments)

    async def list_profiles(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['listProfiles'], arguments)

    async def create_profile(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['createProfile'], arguments)

    async def get_profile(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getProfile'], arguments)

    async def update_profile(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['updateProfile'], arguments)

    async def delete_profile(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['deleteProfile'], arguments)

    async def list_pools(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['listPools'], arguments)

    async def create_pool(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['createPool'], arguments)

    async def get_pool(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getPool'], arguments)

    async def update_pool(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['updatePool'], arguments)

    async def delete_pool(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['deletePool'], arguments)

    async def acquire_instance_lease(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['acquireInstanceLease'], arguments)

    async def release_instance_lease(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['releaseInstanceLease'], arguments)

    async def provision_user_instance(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['provisionUserInstance'], arguments)

    async def get_provisioning_job(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getProvisioningJob'], arguments)


class AsyncImagesAPI(_AsyncAPI):
    async def list_image_recipes(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['listImageRecipes'], arguments)

    async def create_image_recipe(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['createImageRecipe'], arguments)

    async def get_image_recipe(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getImageRecipe'], arguments)

    async def delete_image_recipe(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['deleteImageRecipe'], arguments)

    async def list_image_builds(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['listImageBuilds'], arguments)

    async def start_image_build(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['startImageBuild'], arguments)

    async def get_image_build(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getImageBuild'], arguments)

    async def cancel_image_build(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['cancelImageBuild'], arguments)

    def stream_image_build_logs(self, **arguments: Any) -> AsyncIterator[dict[str, Any]]:
        return self._transport.stream(BY_ID['streamImageBuildLogs'], arguments)

    async def list_managed_images(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['listManagedImages'], arguments)

    async def get_managed_image(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getManagedImage'], arguments)

    async def delete_managed_image(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['deleteManagedImage'], arguments)


class AsyncInferenceAPI(_AsyncAPI):
    async def create_chat_completion(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['createChatCompletion'], arguments)

    async def create_completion(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['createCompletion'], arguments)


class AsyncRuntimeAPI(_AsyncAPI):
    async def get_instance_runtime_capabilities(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getInstanceRuntimeCapabilities'], arguments)

    async def list_sessions(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['listSessions'], arguments)

    async def create_session(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['createSession'], arguments)

    async def get_session(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getSession'], arguments)

    async def delete_session(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['deleteSession'], arguments)

    async def act_on_session(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['actOnSession'], arguments)

    async def submit_turn(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['submitTurn'], arguments)

    async def get_turn(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getTurn'], arguments)

    async def act_on_turn(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['actOnTurn'], arguments)

    def stream_session_events(self, **arguments: Any) -> AsyncIterator[dict[str, Any]]:
        return self._transport.stream(BY_ID['streamSessionEvents'], arguments)

    async def invoke_hermes_rpc(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['invokeHermesRpc'], arguments)


class AsyncToolsAPI(_AsyncAPI):
    async def list_tool_bundles(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['listToolBundles'], arguments)

    async def create_tool_bundle(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['createToolBundle'], arguments)

    async def get_tool_bundle(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getToolBundle'], arguments)

    async def replace_tool_bundle(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['replaceToolBundle'], arguments)

    async def delete_tool_bundle(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['deleteToolBundle'], arguments)

    async def list_tool_bindings(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['listToolBindings'], arguments)

    async def create_tool_binding(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['createToolBinding'], arguments)

    async def get_tool_binding(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getToolBinding'], arguments)

    async def delete_tool_binding(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['deleteToolBinding'], arguments)

    async def list_mcp_servers(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['listMcpServers'], arguments)

    async def create_mcp_server(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['createMcpServer'], arguments)

    async def get_mcp_server(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['getMcpServer'], arguments)

    async def replace_mcp_server(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['replaceMcpServer'], arguments)

    async def delete_mcp_server(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['deleteMcpServer'], arguments)

    async def act_on_mcp_server(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['actOnMcpServer'], arguments)

    async def execute_tool_call(self, **arguments: Any) -> Any:
        return await self._transport.invoke(BY_ID['executeToolCall'], arguments)


class AsyncGatewayAPI(_AsyncAPI):
    _operation: Mapping[str, Any] = {'operation_id': 'invokeHermesRpc', 'method': 'POST', 'path': '/v1/instances/{instanceId}/profiles/{profileId}/rpc', 'path_parameters': ['instanceId', 'profileId'], 'query_parameters': [], 'header_parameters': []}
    methods = tuple(HERMES_RPC_METHODS)

    async def invoke(
        self, method: str, *, instance_id: str, profile_id: str, params: Any = None
    ) -> Any:
        request = {'jsonrpc': '2.0', 'id': 1, 'method': method}
        if params is not None:
            request['params'] = params
        return await self._transport.invoke(
            self._operation,
            {'instance_id': instance_id, 'profile_id': profile_id, 'body': request},
        )

    async def agents_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('agents.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def approval_pending(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('approval.pending', instance_id=instance_id, profile_id=profile_id, params=params)

    async def approval_received(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('approval.received', instance_id=instance_id, profile_id=profile_id, params=params)

    async def approval_respond(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('approval.respond', instance_id=instance_id, profile_id=profile_id, params=params)

    async def billing_auto_reload(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('billing.auto_reload', instance_id=instance_id, profile_id=profile_id, params=params)

    async def billing_charge(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('billing.charge', instance_id=instance_id, profile_id=profile_id, params=params)

    async def billing_charge_status(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('billing.charge_status', instance_id=instance_id, profile_id=profile_id, params=params)

    async def billing_state(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('billing.state', instance_id=instance_id, profile_id=profile_id, params=params)

    async def billing_step_up(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('billing.step_up', instance_id=instance_id, profile_id=profile_id, params=params)

    async def bot_relay_deliver(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('bot_relay.deliver', instance_id=instance_id, profile_id=profile_id, params=params)

    async def bot_relay_outbox_drain(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('bot_relay.outbox.drain', instance_id=instance_id, profile_id=profile_id, params=params)

    async def bot_relay_reply(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('bot_relay.reply', instance_id=instance_id, profile_id=profile_id, params=params)

    async def bot_relay_roster_sync(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('bot_relay.roster.sync', instance_id=instance_id, profile_id=profile_id, params=params)

    async def browser_controller_detach(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('browser.controller.detach', instance_id=instance_id, profile_id=profile_id, params=params)

    async def browser_controller_heartbeat(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('browser.controller.heartbeat', instance_id=instance_id, profile_id=profile_id, params=params)

    async def browser_controller_register(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('browser.controller.register', instance_id=instance_id, profile_id=profile_id, params=params)

    async def browser_controller_result(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('browser.controller.result', instance_id=instance_id, profile_id=profile_id, params=params)

    async def browser_manage(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('browser.manage', instance_id=instance_id, profile_id=profile_id, params=params)

    async def clarify_lock(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('clarify.lock', instance_id=instance_id, profile_id=profile_id, params=params)

    async def cli_exec(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('cli.exec', instance_id=instance_id, profile_id=profile_id, params=params)

    async def client_capabilities(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('client.capabilities', instance_id=instance_id, profile_id=profile_id, params=params)

    async def clipboard_paste(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('clipboard.paste', instance_id=instance_id, profile_id=profile_id, params=params)

    async def command_dispatch(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('command.dispatch', instance_id=instance_id, profile_id=profile_id, params=params)

    async def command_resolve(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('command.resolve', instance_id=instance_id, profile_id=profile_id, params=params)

    async def commands_catalog(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('commands.catalog', instance_id=instance_id, profile_id=profile_id, params=params)

    async def complete_path(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('complete.path', instance_id=instance_id, profile_id=profile_id, params=params)

    async def complete_slash(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('complete.slash', instance_id=instance_id, profile_id=profile_id, params=params)

    async def config_get(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('config.get', instance_id=instance_id, profile_id=profile_id, params=params)

    async def config_set(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('config.set', instance_id=instance_id, profile_id=profile_id, params=params)

    async def config_show(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('config.show', instance_id=instance_id, profile_id=profile_id, params=params)

    async def connection_respond(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('connection.respond', instance_id=instance_id, profile_id=profile_id, params=params)

    async def connectors_connect(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('connectors.connect', instance_id=instance_id, profile_id=profile_id, params=params)

    async def connectors_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('connectors.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def connectors_operation_status(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('connectors.operation.status', instance_id=instance_id, profile_id=profile_id, params=params)

    async def connectors_operation_wake(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('connectors.operation.wake', instance_id=instance_id, profile_id=profile_id, params=params)

    async def cron_manage(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('cron.manage', instance_id=instance_id, profile_id=profile_id, params=params)

    async def delegation_pause(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('delegation.pause', instance_id=instance_id, profile_id=profile_id, params=params)

    async def delegation_status(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('delegation.status', instance_id=instance_id, profile_id=profile_id, params=params)

    async def diagnostics_share_nous(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('diagnostics.share_nous', instance_id=instance_id, profile_id=profile_id, params=params)

    async def file_attach(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('file.attach', instance_id=instance_id, profile_id=profile_id, params=params)

    async def free_tier_ack_notice(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('free_tier.ack_notice', instance_id=instance_id, profile_id=profile_id, params=params)

    async def free_tier_provision(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('free_tier.provision', instance_id=instance_id, profile_id=profile_id, params=params)

    async def free_tier_status(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('free_tier.status', instance_id=instance_id, profile_id=profile_id, params=params)

    async def gateway_capabilities(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('gateway.capabilities', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_approve(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.approve', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_capabilities(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.capabilities', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_create(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.create', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_demote(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.demote', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_disband(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.disband', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_log(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.log', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_peer_invite(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.peer.invite', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_peer_register(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.peer.register', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_peer_revoke(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.peer.revoke', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_promote(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.promote', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_rename(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.rename', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_replica_state(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.replica_state', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_replicate(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.replicate', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_retry(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.retry', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_send(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.send', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_state(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.state', instance_id=instance_id, profile_id=profile_id, params=params)

    async def groups_stop(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('groups.stop', instance_id=instance_id, profile_id=profile_id, params=params)

    async def handoff_fail(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('handoff.fail', instance_id=instance_id, profile_id=profile_id, params=params)

    async def handoff_request(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('handoff.request', instance_id=instance_id, profile_id=profile_id, params=params)

    async def handoff_state(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('handoff.state', instance_id=instance_id, profile_id=profile_id, params=params)

    async def image_attach(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('image.attach', instance_id=instance_id, profile_id=profile_id, params=params)

    async def image_attach_bytes(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('image.attach_bytes', instance_id=instance_id, profile_id=profile_id, params=params)

    async def image_detach(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('image.detach', instance_id=instance_id, profile_id=profile_id, params=params)

    async def image_generate(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('image.generate', instance_id=instance_id, profile_id=profile_id, params=params)

    async def input_detect_drop(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('input.detect_drop', instance_id=instance_id, profile_id=profile_id, params=params)

    async def insights_get(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('insights.get', instance_id=instance_id, profile_id=profile_id, params=params)

    async def learning_delete(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('learning.delete', instance_id=instance_id, profile_id=profile_id, params=params)

    async def learning_detail(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('learning.detail', instance_id=instance_id, profile_id=profile_id, params=params)

    async def learning_edit(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('learning.edit', instance_id=instance_id, profile_id=profile_id, params=params)

    async def learning_frames(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('learning.frames', instance_id=instance_id, profile_id=profile_id, params=params)

    async def llm_oneshot(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('llm.oneshot', instance_id=instance_id, profile_id=profile_id, params=params)

    async def mcp_catalog(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('mcp.catalog', instance_id=instance_id, profile_id=profile_id, params=params)

    async def mcp_servers_add(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('mcp.servers.add', instance_id=instance_id, profile_id=profile_id, params=params)

    async def mcp_servers_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('mcp.servers.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def mcp_servers_oauth_callback(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('mcp.servers.oauth.callback', instance_id=instance_id, profile_id=profile_id, params=params)

    async def mcp_servers_oauth_cancel(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('mcp.servers.oauth.cancel', instance_id=instance_id, profile_id=profile_id, params=params)

    async def mcp_servers_oauth_poll(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('mcp.servers.oauth.poll', instance_id=instance_id, profile_id=profile_id, params=params)

    async def mcp_servers_oauth_start(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('mcp.servers.oauth.start', instance_id=instance_id, profile_id=profile_id, params=params)

    async def mcp_servers_remove(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('mcp.servers.remove', instance_id=instance_id, profile_id=profile_id, params=params)

    async def mcp_servers_set_api_key(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('mcp.servers.set_api_key', instance_id=instance_id, profile_id=profile_id, params=params)

    async def mcp_servers_status(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('mcp.servers.status', instance_id=instance_id, profile_id=profile_id, params=params)

    async def mcp_servers_test(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('mcp.servers.test', instance_id=instance_id, profile_id=profile_id, params=params)

    async def message_react(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('message.react', instance_id=instance_id, profile_id=profile_id, params=params)

    async def model_disconnect(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('model.disconnect', instance_id=instance_id, profile_id=profile_id, params=params)

    async def model_options(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('model.options', instance_id=instance_id, profile_id=profile_id, params=params)

    async def model_save_key(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('model.save_key', instance_id=instance_id, profile_id=profile_id, params=params)

    async def paste_collapse(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('paste.collapse', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pdf_attach(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pdf.attach', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_cancel(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.cancel', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_cells(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.cells', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_disable(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.disable', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_export(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.export', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_gallery(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.gallery', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_generate(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.generate', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_generate_status(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.generate.status', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_hatch(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.hatch', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_info(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.info', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_info_meta(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.info.meta', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_remove(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.remove', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_rename(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.rename', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_scale(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.scale', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_select(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.select', instance_id=instance_id, profile_id=profile_id, params=params)

    async def pet_thumb(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('pet.thumb', instance_id=instance_id, profile_id=profile_id, params=params)

    async def ping(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('ping', instance_id=instance_id, profile_id=profile_id, params=params)

    async def plugins_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('plugins.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def plugins_manage(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('plugins.manage', instance_id=instance_id, profile_id=profile_id, params=params)

    async def preview_restart(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('preview.restart', instance_id=instance_id, profile_id=profile_id, params=params)

    async def process_kill(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('process.kill', instance_id=instance_id, profile_id=profile_id, params=params)

    async def process_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('process.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def process_stop(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('process.stop', instance_id=instance_id, profile_id=profile_id, params=params)

    async def profiles_configure(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('profiles.configure', instance_id=instance_id, profile_id=profile_id, params=params)

    async def profiles_create(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('profiles.create', instance_id=instance_id, profile_id=profile_id, params=params)

    async def profiles_describe(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('profiles.describe', instance_id=instance_id, profile_id=profile_id, params=params)

    async def profiles_get_asset(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('profiles.get_asset', instance_id=instance_id, profile_id=profile_id, params=params)

    async def profiles_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('profiles.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def profiles_remember_onboarding(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('profiles.remember_onboarding', instance_id=instance_id, profile_id=profile_id, params=params)

    async def profiles_set_asset(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('profiles.set_asset', instance_id=instance_id, profile_id=profile_id, params=params)

    async def project_facts(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('project.facts', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_add_folder(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.add_folder', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_archive(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.archive', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_create(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.create', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_delete(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.delete', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_discover_repos(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.discover_repos', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_for_cwd(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.for_cwd', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_get(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.get', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_project_sessions(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.project_sessions', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_record_repos(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.record_repos', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_remove_folder(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.remove_folder', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_set_active(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.set_active', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_set_primary(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.set_primary', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_tree(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.tree', instance_id=instance_id, profile_id=profile_id, params=params)

    async def projects_update(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('projects.update', instance_id=instance_id, profile_id=profile_id, params=params)

    async def prompt_background(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('prompt.background', instance_id=instance_id, profile_id=profile_id, params=params)

    async def prompt_btw(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('prompt.btw', instance_id=instance_id, profile_id=profile_id, params=params)

    async def prompt_submit(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('prompt.submit', instance_id=instance_id, profile_id=profile_id, params=params)

    async def reload_env(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('reload.env', instance_id=instance_id, profile_id=profile_id, params=params)

    async def reload_mcp(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('reload.mcp', instance_id=instance_id, profile_id=profile_id, params=params)

    async def request_answer(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('request.answer', instance_id=instance_id, profile_id=profile_id, params=params)

    async def rollback_diff(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('rollback.diff', instance_id=instance_id, profile_id=profile_id, params=params)

    async def rollback_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('rollback.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def rollback_restore(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('rollback.restore', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_activate(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.activate', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_active_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.active_list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_branch(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.branch', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_close(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.close', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_compress(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.compress', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_context_breakdown(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.context_breakdown', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_control(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.control', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_control_read(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.control.read', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_create(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.create', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_cwd_set(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.cwd.set', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_delete(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.delete', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_events_since(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.events.since', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_events_stats(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.events.stats', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_foreign_import(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.foreign.import', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_foreign_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.foreign.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_foreign_preview(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.foreign.preview', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_history(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.history', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_interrupt(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.interrupt', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_most_recent(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.most_recent', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_redirect(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.redirect', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_resume(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.resume', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_save(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.save', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_set_hidden(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.set_hidden', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_status(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.status', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_steer(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.steer', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_title(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.title', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_undo(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.undo', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_usage(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.usage', instance_id=instance_id, profile_id=profile_id, params=params)

    async def session_workspace_move(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('session.workspace.move', instance_id=instance_id, profile_id=profile_id, params=params)

    async def setup_runtime_check(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('setup.runtime_check', instance_id=instance_id, profile_id=profile_id, params=params)

    async def setup_status(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('setup.status', instance_id=instance_id, profile_id=profile_id, params=params)

    async def shell_exec(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('shell.exec', instance_id=instance_id, profile_id=profile_id, params=params)

    async def skills_manage(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('skills.manage', instance_id=instance_id, profile_id=profile_id, params=params)

    async def skills_reload(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('skills.reload', instance_id=instance_id, profile_id=profile_id, params=params)

    async def slash_exec(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('slash.exec', instance_id=instance_id, profile_id=profile_id, params=params)

    async def spawn_tree_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('spawn_tree.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def spawn_tree_load(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('spawn_tree.load', instance_id=instance_id, profile_id=profile_id, params=params)

    async def spawn_tree_save(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('spawn_tree.save', instance_id=instance_id, profile_id=profile_id, params=params)

    async def subagent_interrupt(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('subagent.interrupt', instance_id=instance_id, profile_id=profile_id, params=params)

    async def subagent_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('subagent.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def subagent_steer(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('subagent.steer', instance_id=instance_id, profile_id=profile_id, params=params)

    async def subagent_tail(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('subagent.tail', instance_id=instance_id, profile_id=profile_id, params=params)

    async def subscription_change(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('subscription.change', instance_id=instance_id, profile_id=profile_id, params=params)

    async def subscription_preview(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('subscription.preview', instance_id=instance_id, profile_id=profile_id, params=params)

    async def subscription_resume(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('subscription.resume', instance_id=instance_id, profile_id=profile_id, params=params)

    async def subscription_state(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('subscription.state', instance_id=instance_id, profile_id=profile_id, params=params)

    async def subscription_upgrade(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('subscription.upgrade', instance_id=instance_id, profile_id=profile_id, params=params)

    async def system_battery(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('system.battery', instance_id=instance_id, profile_id=profile_id, params=params)

    async def terminal_resize(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('terminal.resize', instance_id=instance_id, profile_id=profile_id, params=params)

    async def tools_configure(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('tools.configure', instance_id=instance_id, profile_id=profile_id, params=params)

    async def tools_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('tools.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def tools_show(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('tools.show', instance_id=instance_id, profile_id=profile_id, params=params)

    async def toolsets_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('toolsets.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def usage_bars(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('usage.bars', instance_id=instance_id, profile_id=profile_id, params=params)

    async def vault_add(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('vault.add', instance_id=instance_id, profile_id=profile_id, params=params)

    async def vault_list(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('vault.list', instance_id=instance_id, profile_id=profile_id, params=params)

    async def vault_lock(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('vault.lock', instance_id=instance_id, profile_id=profile_id, params=params)

    async def vault_remove(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('vault.remove', instance_id=instance_id, profile_id=profile_id, params=params)

    async def vault_source_set(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('vault.source.set', instance_id=instance_id, profile_id=profile_id, params=params)

    async def vault_sources(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('vault.sources', instance_id=instance_id, profile_id=profile_id, params=params)

    async def vault_unlock(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('vault.unlock', instance_id=instance_id, profile_id=profile_id, params=params)

    async def verification_status(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('verification.status', instance_id=instance_id, profile_id=profile_id, params=params)

    async def voice_record(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('voice.record', instance_id=instance_id, profile_id=profile_id, params=params)

    async def voice_toggle(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('voice.toggle', instance_id=instance_id, profile_id=profile_id, params=params)

    async def voice_tts(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('voice.tts', instance_id=instance_id, profile_id=profile_id, params=params)

    async def wake_feed(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('wake.feed', instance_id=instance_id, profile_id=profile_id, params=params)

    async def wake_pause(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('wake.pause', instance_id=instance_id, profile_id=profile_id, params=params)

    async def wake_resume(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('wake.resume', instance_id=instance_id, profile_id=profile_id, params=params)

    async def wake_start(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('wake.start', instance_id=instance_id, profile_id=profile_id, params=params)

    async def wake_status(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('wake.status', instance_id=instance_id, profile_id=profile_id, params=params)

    async def wake_stop(
        self, *, instance_id: str, profile_id: str, **params: Any
    ) -> Any:
        return await self.invoke('wake.stop', instance_id=instance_id, profile_id=profile_id, params=params)
