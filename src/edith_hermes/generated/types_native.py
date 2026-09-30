"""Generated wire-shape types; required keys are explicit. Do not edit."""
from __future__ import annotations
import builtins
from typing import Any, Literal, Union
from typing_extensions import Required, TypedDict, TypeAlias
from . import types_control_plane
from . import types_images
from . import types_runtime
from . import types_tools
from . import types_providers
from . import types_inference

ActiveIdResult = TypedDict('ActiveIdResult', {
    'active_id': 'Union[str, None]',
}, total=False)

ActiveSubagent = TypedDict('ActiveSubagent', {
    'subagent_id': Required['str'],
    'parent_id': 'Union[str, None]',
    'depth': 'Union[int, None]',
    'goal': 'Union[str, None]',
    'delegation_id': 'Union[str, None]',
    'model': 'Union[str, None]',
    'started_at': 'Union[float, None]',
    'status': 'Union[str, None]',
    'tool_count': 'Union[int, None]',
    'owner_agent_session_id': 'Union[str, None]',
}, total=False)

AgentPluginRow = TypedDict('AgentPluginRow', {
    'name': Required['str'],
    'key': Required['str'],
    'version': Required['str'],
    'description': Required['str'],
    'source': Required['str'],
    'status': Required['str'],
    'portable': Required['bool'],
    'install_dir': Required['str'],
    'has_desktop_half': Required['bool'],
    'catalog_name': 'Union[str, None]',
    'catalog_tier': 'Union[str, None]',
    'installed_sha': 'Union[str, None]',
    'catalog_sha': 'Union[str, None]',
    'catalog_version': 'Union[str, None]',
    'update_available': 'Union[bool, None]',
    'pinned_sha': 'Union[str, None]',
}, total=False)

AgentProcessRow = TypedDict('AgentProcessRow', {
    'session_id': Required['str'],
    'command': Required['str'],
    'status': Required['str'],
    'uptime': Required['int'],
}, total=False)

AgentsListParams = TypedDict('AgentsListParams', {
    'profile': 'Union[str, None]',
}, total=False)

AgentsListResult = TypedDict('AgentsListResult', {
    'processes': 'builtins.list[AgentProcessRow]',
}, total=False)

ApprovalPendingParams = TypedDict('ApprovalPendingParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

ApprovalPendingResult = TypedDict('ApprovalPendingResult', {
    'approvals': Required['builtins.list[PendingApproval]'],
}, total=False)

ApprovalReceivedParams = TypedDict('ApprovalReceivedParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'request_id': Required['str'],
}, total=False)

ApprovalReceivedResult = TypedDict('ApprovalReceivedResult', {
    'acknowledged': Required['bool'],
}, total=False)

ApprovalRequestParams = TypedDict('ApprovalRequestParams', {
    'session_id': Required['str'],
    'request_id': Required['str'],
    'command': 'str',
    'description': 'str',
    'choices': 'builtins.list[ApprovalChoice]',
    'allow_permanent': 'Union[bool, None]',
    'allow_session': 'Union[bool, None]',
    'smart_denied': 'Union[bool, None]',
    'tool_name': 'Union[str, None]',
    'gateway_session_id': 'Union[str, None]',
}, total=False)

ApprovalRespondParams = TypedDict('ApprovalRespondParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'choice': 'Union[str, None]',
    'all': 'Union[bool, None]',
    'request_id': 'Union[str, None]',
}, total=False)

ApprovalRespondResult = TypedDict('ApprovalRespondResult', {
    'resolved': Required['int'],
}, total=False)

ApprovalResult = TypedDict('ApprovalResult', {
    'choice': Required['ApprovalChoice'],
    'all': 'Union[bool, None]',
}, total=False)

AttachedImageResult = TypedDict('AttachedImageResult', {
    'name': 'Union[str, None]',
    'width': 'Union[int, None]',
    'height': 'Union[int, None]',
    'token_estimate': 'Union[int, None]',
    'attached': Required['bool'],
    'path': 'Union[str, None]',
    'count': 'Union[int, None]',
    'remainder': 'Union[str, None]',
    'text': 'Union[str, None]',
    'bytes': 'Union[int, None]',
    'message': 'Union[str, None]',
}, total=False)

AutoContinue = TypedDict('AutoContinue', {
    'attempt': Required['int'],
    'interrupted_at': Required['float'],
}, total=False)

BillingAutoReload = TypedDict('BillingAutoReload', {
    'enabled': Required['bool'],
    'threshold_usd': 'Union[str, None]',
    'threshold_display': Required['str'],
    'reload_to_usd': 'Union[str, None]',
    'reload_to_display': Required['str'],
    'card': 'Union[BillingAutoReloadCard, None]',
}, total=False)

BillingAutoReloadCard = TypedDict('BillingAutoReloadCard', {
    'kind': Required['AutoReloadCardKind'],
    'payment_method_id': 'Union[str, None]',
    'brand': 'Union[str, None]',
    'last4': 'Union[str, None]',
}, total=False)

BillingAutoReloadParams = TypedDict('BillingAutoReloadParams', {
    'profile': 'Union[str, None]',
    'enabled': 'bool',
    'threshold': 'Union[float, str, None]',
    'top_up_amount': 'Union[float, str, None]',
}, total=False)

BillingBlock = TypedDict('BillingBlock', {
    'provider': Required['str'],
    'provider_label': Required['str'],
    'model': Required['str'],
    'billing_url': Required['Union[str, None]'],
    'is_nous': Required['bool'],
    'message': Required['str'],
    'unverified': 'Union[bool, None]',
}, total=False)

BillingCardInfo = TypedDict('BillingCardInfo', {
    'brand': Required['str'],
    'last4': Required['str'],
    'masked': Required['str'],
    'display': 'Union[str, None]',
    'resolved_via': 'Union[str, None]',
}, total=False)

BillingChargeParams = TypedDict('BillingChargeParams', {
    'profile': 'Union[str, None]',
    'amount_usd': 'Union[float, str, None]',
    'idempotency_key': 'Union[str, None]',
}, total=False)

BillingChargeResult = TypedDict('BillingChargeResult', {
    'ok': Required['bool'],
    'error': 'Union[str, None]',
    'message': 'Union[str, None]',
    'portal_url': 'Union[str, None]',
    'retry_after': 'Union[int, float, None]',
    'payload': 'Union[dict[str, Any], None]',
    'actor': 'Union[str, None]',
    'code': 'Union[str, None]',
    'recovery': 'Union[str, None]',
    'charge_id': 'Union[str, None]',
    'idempotency_key': 'Union[str, None]',
}, total=False)

BillingChargeStatusParams = TypedDict('BillingChargeStatusParams', {
    'profile': 'Union[str, None]',
    'charge_id': 'Union[str, None]',
}, total=False)

BillingChargeStatusResult = TypedDict('BillingChargeStatusResult', {
    'ok': Required['bool'],
    'error': 'Union[str, None]',
    'message': 'Union[str, None]',
    'portal_url': 'Union[str, None]',
    'retry_after': 'Union[int, float, None]',
    'payload': 'Union[dict[str, Any], None]',
    'actor': 'Union[str, None]',
    'code': 'Union[str, None]',
    'recovery': 'Union[str, None]',
    'status': 'Union[str, None]',
    'amount_usd': 'Union[str, float, None]',
    'settled_at': 'Union[str, None]',
    'reason': 'Union[str, None]',
}, total=False)

BillingMonthlyCap = TypedDict('BillingMonthlyCap', {
    'limit_usd': 'Union[str, None]',
    'limit_display': Required['str'],
    'spent_this_month_usd': 'Union[str, None]',
    'spent_display': Required['str'],
    'is_default_ceiling': Required['bool'],
}, total=False)

BillingMutationResult = TypedDict('BillingMutationResult', {
    'ok': Required['bool'],
    'error': 'Union[str, None]',
    'message': 'Union[str, None]',
    'portal_url': 'Union[str, None]',
    'retry_after': 'Union[int, float, None]',
    'payload': 'Union[dict[str, Any], None]',
    'actor': 'Union[str, None]',
    'code': 'Union[str, None]',
    'recovery': 'Union[str, None]',
}, total=False)

BillingPaymentMethod = TypedDict('BillingPaymentMethod', {
    'kind': Required['PaymentMethodKind'],
    'brand': 'Union[str, None]',
    'last4': 'Union[str, None]',
    'wallet': 'Union[str, None]',
    'email': 'Union[str, None]',
    'raw_kind': 'Union[str, None]',
    'resolved_via': 'Union[str, None]',
}, total=False)

BillingPendingChangeResult = TypedDict('BillingPendingChangeResult', {
    'ok': Required['bool'],
    'error': 'Union[str, None]',
    'message': 'Union[str, None]',
    'portal_url': 'Union[str, None]',
    'retry_after': 'Union[int, float, None]',
    'payload': 'Union[dict[str, Any], None]',
    'actor': 'Union[str, None]',
    'code': 'Union[str, None]',
    'recovery': 'Union[str, None]',
}, total=False)

BillingStateResult = TypedDict('BillingStateResult', {
    'ok': Required['bool'],
    'logged_in': Required['bool'],
    'free_tier': 'bool',
    'free_tier_model': 'Union[str, None]',
    'org_name': 'Union[str, None]',
    'org_slug': 'Union[str, None]',
    'role': 'Union[str, None]',
    'is_admin': 'Union[bool, None]',
    'can_change_plan': 'Union[bool, None]',
    'can_charge': 'Union[bool, None]',
    'balance_usd': 'Union[str, None]',
    'balance_display': 'Union[str, None]',
    'cli_billing_enabled': 'Union[bool, None]',
    'charge_presets': 'Union[builtins.list[str], None]',
    'charge_presets_display': 'Union[builtins.list[str], None]',
    'min_usd': 'Union[str, None]',
    'max_usd': 'Union[str, None]',
    'card': 'Union[BillingCardInfo, None]',
    'payment_method': 'Union[BillingPaymentMethod, None]',
    'monthly_cap': 'Union[BillingMonthlyCap, None]',
    'auto_reload': 'Union[BillingAutoReload, None]',
    'portal_url': 'Union[str, None]',
    'error': 'Union[str, None]',
    'usage': 'Union[UsageModel, None]',
}, total=False)

BillingStepUpParams = TypedDict('BillingStepUpParams', {
    'profile': 'Union[str, None]',
    'session_id': 'Union[str, None]',
}, total=False)

BillingStepUpResult = TypedDict('BillingStepUpResult', {
    'ok': Required['bool'],
    'error': 'Union[str, None]',
    'message': 'Union[str, None]',
    'portal_url': 'Union[str, None]',
    'retry_after': 'Union[int, float, None]',
    'payload': 'Union[dict[str, Any], None]',
    'actor': 'Union[str, None]',
    'code': 'Union[str, None]',
    'recovery': 'Union[str, None]',
    'granted': 'Union[bool, None]',
}, total=False)

BillingStepUpVerificationPayload = TypedDict('BillingStepUpVerificationPayload', {
    'verification_url': Required['str'],
    'user_code': Required['str'],
}, total=False)

BotRelayDeliverParams = TypedDict('BotRelayDeliverParams', {
    'profile': Required['str'],
    'message': Required['str'],
    'from_profile': 'Union[str, None]',
    'from_handle': 'Union[str, None]',
    'from_connection': 'Union[str, None]',
}, total=False)

BotRelayDeliverResult = TypedDict('BotRelayDeliverResult', {
    'reply': Required['str'],
}, total=False)

BotRelayOutboxDrainParams = TypedDict('BotRelayOutboxDrainParams', {
    'profile': 'Union[str, None]',
}, total=False)

BotRelayOutboxDrainResult = TypedDict('BotRelayOutboxDrainResult', {
    'envelopes': Required['builtins.list[RelayEnvelope]'],
}, total=False)

BotRelayReplyParams = TypedDict('BotRelayReplyParams', {
    'profile': 'Union[str, None]',
    'id': Required['str'],
    'reply': 'Union[str, None]',
    'error': 'Union[str, None]',
    'reason': 'Union[str, None]',
}, total=False)

BotRelayRosterSyncParams = TypedDict('BotRelayRosterSyncParams', {
    'profile': 'Union[str, None]',
    'agents': 'Union[builtins.list[RelayAgentRow], None]',
}, total=False)

BotRelayRosterSyncResult = TypedDict('BotRelayRosterSyncResult', {
    'count': Required['int'],
}, total=False)

BrowserControllerCancelPayload = TypedDict('BrowserControllerCancelPayload', {
    'command_id': Required['str'],
    'tool_call_id': 'Union[str, None]',
}, total=False)

BrowserControllerCommandPayload = TypedDict('BrowserControllerCommandPayload', {
    'command_id': Required['str'],
    'action': Required['str'],
    'arguments': Required['dict[str, Any]'],
    'controller_id': 'Union[str, None]',
    'browser_profile_id': 'Union[str, None]',
    'tool_call_id': 'Union[str, None]',
}, total=False)

BrowserControllerDetachResult = TypedDict('BrowserControllerDetachResult', {
    'detached': 'bool',
}, total=False)

BrowserControllerParams = TypedDict('BrowserControllerParams', {
    'session_id': Required['str'],
}, total=False)

BrowserControllerRegisterParams = TypedDict('BrowserControllerRegisterParams', {
    'session_id': Required['str'],
    'controller_id': Required['str'],
    'browser_profile_id': Required['str'],
    'capabilities': 'Union[builtins.list[str], None]',
    'protocol_version': 'Union[Any, None]',
    'principal_id': 'Union[str, None]',
}, total=False)

BrowserControllerRegisterResult = TypedDict('BrowserControllerRegisterResult', {
    'scope': Required['ControllerScope'],
}, total=False)

BrowserControllerResultParams = TypedDict('BrowserControllerResultParams', {
    'session_id': Required['str'],
    'command_id': Required['str'],
    'ok': 'Union[Any, None]',
    'result': 'Union[Any, None]',
    'error': 'Union[Any, None]',
}, total=False)

BrowserControllerResultResult = TypedDict('BrowserControllerResultResult', {
    'accepted': Required['bool'],
}, total=False)

BrowserManageParams = TypedDict('BrowserManageParams', {
    'action': 'BrowserAction',
    'url': 'Union[str, None]',
    'session_id': 'Union[str, None]',
    'profile': 'Union[str, None]',
}, total=False)

BrowserManageResult = TypedDict('BrowserManageResult', {
    'connected': Required['bool'],
    'url': 'Union[str, None]',
    'messages': 'Union[builtins.list[str], None]',
}, total=False)

BrowserProgressPayload = TypedDict('BrowserProgressPayload', {
    'message': Required['str'],
    'level': Required['str'],
}, total=False)

CapabilityEntry = TypedDict('CapabilityEntry', {
    'name': Required['str'],
    'enabled': 'bool',
}, total=False)

ChangeSignalPayload = TypedDict('ChangeSignalPayload', {

}, total=False)

ClarifyLockParams = TypedDict('ClarifyLockParams', {
    'request_id': Required['str'],
    'question_id': Required['str'],
    'answer': 'Any',
    'profile': 'Union[str, None]',
}, total=False)

ClarifyLockResult = TypedDict('ClarifyLockResult', {
    'status': Required['ClarifyLockStatus'],
    'remaining': 'Union[builtins.list[str], None]',
}, total=False)

ClarifyQuestion = TypedDict('ClarifyQuestion', {
    'qid': Required['str'],
    'question': Required['str'],
    'choices': 'Union[builtins.list[str], None]',
    'multi_select': 'bool',
}, total=False)

ClarifyRequestParams = TypedDict('ClarifyRequestParams', {
    'session_id': Required['str'],
    'question': 'Union[str, None]',
    'choices': 'Union[builtins.list[str], None]',
    'multi_select': 'Union[bool, None]',
    'questions': 'Union[builtins.list[ClarifyQuestion], None]',
    'answers': 'Union[dict[str, str], None]',
}, total=False)

ClarifyResult = TypedDict('ClarifyResult', {
    'answer': 'Union[str, None]',
    'answers': 'Union[dict[str, str], None]',
}, total=False)

CliExecParams = TypedDict('CliExecParams', {
    'argv': Required['builtins.list[str]'],
    'timeout': 'Union[int, None]',
    'profile': 'Union[str, None]',
}, total=False)

CliExecResult = TypedDict('CliExecResult', {
    'blocked': Required['bool'],
    'code': Required['int'],
    'output': Required['str'],
    'hint': 'Union[str, None]',
}, total=False)

ClientCapabilitiesParams = TypedDict('ClientCapabilitiesParams', {
    'server_requests': 'bool',
}, total=False)

ClientCapabilitiesResult = TypedDict('ClientCapabilitiesResult', {
    'server_requests': Required['builtins.list[str]'],
}, total=False)

ClipboardPasteParams = TypedDict('ClipboardPasteParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

CommandCatalogMeta = TypedDict('CommandCatalogMeta', {
    'argument_mode': 'Union[ArgumentMode, None]',
    'desktop': 'Union[str, None]',
}, total=False)

CommandCategory = TypedDict('CommandCategory', {
    'name': Required['str'],
    'pairs': 'builtins.list[builtins.list[str]]',
}, total=False)

CommandDispatchParams = TypedDict('CommandDispatchParams', {
    'name': Required['str'],
    'arg': 'Union[str, None]',
    'session_id': 'Union[str, None]',
    'profile': 'Union[str, None]',
}, total=False)

CommandDispatchResult = TypedDict('CommandDispatchResult', {
    'type': Required['DispatchType'],
    'output': 'Union[str, None]',
    'target': 'Union[str, None]',
    'message': 'Union[str, None]',
    'notice': 'Union[str, None]',
    'display': 'Union[str, None]',
    'name': 'Union[str, None]',
    'status': 'Union[str, None]',
}, total=False)

CommandResolveParams = TypedDict('CommandResolveParams', {
    'name': 'Union[str, None]',
    'profile': 'Union[str, None]',
}, total=False)

CommandResolveResult = TypedDict('CommandResolveResult', {
    'canonical': Required['str'],
    'description': Required['str'],
    'category': Required['str'],
}, total=False)

CommandsCatalogParams = TypedDict('CommandsCatalogParams', {
    'session_id': 'Union[str, None]',
    'profile': 'Union[str, None]',
}, total=False)

CommandsCatalogResult = TypedDict('CommandsCatalogResult', {
    'pairs': 'builtins.list[builtins.list[str]]',
    'sub': 'dict[str, builtins.list[str]]',
    'canon': 'dict[str, str]',
    'commands': 'dict[str, CommandCatalogMeta]',
    'categories': 'builtins.list[CommandCategory]',
    'skills': 'dict[str, SkillCatalogEntry]',
    'skill_count': 'int',
    'warning': 'str',
}, total=False)

CompletePathParams = TypedDict('CompletePathParams', {
    'profile': 'Union[str, None]',
    'word': 'Union[str, None]',
    'cwd': 'Union[str, None]',
    'session_id': 'Union[str, None]',
}, total=False)

CompleteSlashParams = TypedDict('CompleteSlashParams', {
    'text': 'Union[str, None]',
    'session_id': 'Union[str, None]',
}, total=False)

CompleteSlashResult = TypedDict('CompleteSlashResult', {
    'items': 'builtins.list[CompletionItem]',
    'replace_from': 'Union[int, None]',
}, total=False)

CompletionItem = TypedDict('CompletionItem', {
    'text': Required['str'],
    'display': 'str',
    'meta': 'str',
    'kind': 'Union[str, None]',
}, total=False)

CompletionItemsResult = TypedDict('CompletionItemsResult', {
    'items': 'builtins.list[CompletionItem]',
}, total=False)

CompressionSummary = TypedDict('CompressionSummary', {
    'noop': 'bool',
    'aborted': 'bool',
    'refused_would_grow': 'Union[bool, None]',
    'fallback_used': 'Union[bool, None]',
    'headline': 'str',
    'token_line': 'str',
    'note': 'Union[str, None]',
}, total=False)

ConfigGetParams = TypedDict('ConfigGetParams', {
    'profile': 'Union[str, None]',
    'key': Required['str'],
    'cwd': 'Union[str, None]',
    'session_id': 'Union[str, None]',
}, total=False)

ConfigGetResult = TypedDict('ConfigGetResult', {
    'value': 'Union[str, None]',
    'display': 'Union[str, None]',
    'tool_progress': 'Union[str, None]',
    'model': 'Union[str, None]',
    'provider': 'Union[str, None]',
    'providers': 'Union[builtins.list[ConfigProviderRef], None]',
    'home': 'Union[str, None]',
    'cwd': 'Union[str, None]',
    'branch': 'Union[str, None]',
    'config': 'Union[dict[str, Any], None]',
    'prompt': 'Union[str, None]',
    'mtime': 'Union[float, None]',
    'mcp_rev': 'Union[str, None]',
}, total=False)

ConfigProviderRef = TypedDict('ConfigProviderRef', {
    'id': Required['str'],
    'label': Required['str'],
    'aliases': 'builtins.list[str]',
    'authenticated': 'bool',
}, total=False)

ConfigSection = TypedDict('ConfigSection', {
    'title': Required['str'],
    'rows': 'builtins.list[builtins.list[str]]',
}, total=False)

ConfigSetParams = TypedDict('ConfigSetParams', {
    'profile': 'Union[str, None]',
    'key': Required['str'],
    'value': 'Any',
    'session_id': 'Union[str, None]',
    'scope': 'Union[str, None]',
    'confirm_expensive_model': 'bool',
}, total=False)

ConfigSetResult = TypedDict('ConfigSetResult', {
    'key': Required['str'],
    'value': 'Union[str, bool, None]',
    'warning': 'Union[str, None]',
    'confirm_required': 'Union[bool, None]',
    'confirm_message': 'Union[str, None]',
    'scope': 'Union[str, None]',
    'deferred': 'Union[bool, None]',
    'tool_progress': 'Union[str, None]',
    'cwd': 'Union[str, None]',
    'branch': 'Union[str, None]',
    'history_reset': 'Union[bool, None]',
    'info': 'Union[SessionLiveInfo, None]',
}, total=False)

ConfigShowParams = TypedDict('ConfigShowParams', {
    'profile': 'Union[str, None]',
}, total=False)

ConfigShowResult = TypedDict('ConfigShowResult', {
    'sections': 'builtins.list[ConfigSection]',
}, total=False)

ConnectionAnswer = TypedDict('ConnectionAnswer', {
    'targets': 'builtins.list[ConnectionAnswerTarget]',
    'settled_by': 'Union[ConnectionSettleReason, None]',
}, total=False)

ConnectionAnswerTarget = TypedDict('ConnectionAnswerTarget', {
    'name': Required['str'],
    'status': Required['ConnectionAnswerStatus'],
    'detail': 'Union[str, None]',
    'env': 'Union[dict[str, str], None]',
}, total=False)

ConnectionOperationParams = TypedDict('ConnectionOperationParams', {
    'profile': 'Union[str, None]',
    'session_id': Required['str'],
    'op_id': Required['str'],
}, total=False)

ConnectionOperationStatus = TypedDict('ConnectionOperationStatus', {
    'op_id': Required['str'],
    'seq': Required['int'],
    'deadline_at': Required['float'],
    'settled': Required['bool'],
    'settled_at': 'Union[float, None]',
    'settled_by': 'Union[ConnectionSettleReason, None]',
    'targets': Required['builtins.list[ConnectionOperationTarget]'],
}, total=False)

ConnectionOperationTarget = TypedDict('ConnectionOperationTarget', {
    'name': Required['str'],
    'kind': Required['ConnectionTargetKind'],
    'action': Required['ConnectionTargetAction'],
    'state': Required['ConnectionTargetState'],
    'detail': 'Union[str, None]',
    'instructions': 'Union[str, None]',
    'discovery_error': 'Union[str, None]',
    'connect_url': 'Union[str, None]',
    'connection_id': 'Union[str, None]',
    'attempt': 'Union[str, None]',
    'required_env': 'Union[builtins.list[ConnectionTargetEnvField], None]',
    'tools': 'Union[builtins.list[str], None]',
    'hint': 'Union[str, None]',
}, total=False)

ConnectionRequestPayload = TypedDict('ConnectionRequestPayload', {
    'op_id': Required['str'],
    'seq': Required['int'],
    'deadline_at': Required['float'],
    'timeout_seconds': Required['float'],
    'targets': Required['builtins.list[ConnectionOperationTarget]'],
    'tool_call_id': 'Union[str, None]',
}, total=False)

ConnectionRespondParams = TypedDict('ConnectionRespondParams', {
    'profile': 'Union[str, None]',
    'session_id': Required['str'],
    'op_id': Required['str'],
    'result': Required['ConnectionAnswer'],
}, total=False)

ConnectionRespondResult = TypedDict('ConnectionRespondResult', {
    'status': Required['str'],
    'settled': Required['bool'],
}, total=False)

ConnectionTargetEnvField = TypedDict('ConnectionTargetEnvField', {
    'name': Required['str'],
    'required': Required['bool'],
    'secret': Required['bool'],
    'default': Required['str'],
    'prompt': 'Union[str, None]',
}, total=False)

ConnectionUpdatePayload = TypedDict('ConnectionUpdatePayload', {
    'op_id': Required['str'],
    'seq': Required['int'],
    'deadline_at': Required['float'],
    'settled': Required['bool'],
    'settled_at': 'Union[float, None]',
    'settled_by': 'Union[ConnectionSettleReason, None]',
    'targets': Required['builtins.list[ConnectionOperationTarget]'],
    'target': 'Union[str, None]',
    'from': 'Union[ConnectionTargetState, None]',
    'to': 'Union[ConnectionTargetState, None]',
    'actor': 'Union[ConnectionActor, None]',
    'detail': 'Union[str, None]',
}, total=False)

ConnectionWakeResult = TypedDict('ConnectionWakeResult', {
    'status': Required['str'],
}, total=False)

ConnectorRow = TypedDict('ConnectorRow', {
    'connector': 'str',
    'connected': 'Union[bool, None]',
    'enabled': 'Union[bool, None]',
    'connectionStatus': 'Union[str, None]',
    'name': 'Union[str, None]',
    'description': 'Union[str, None]',
}, total=False)

ConnectorsConnectParams = TypedDict('ConnectorsConnectParams', {
    'profile': 'Union[str, None]',
    'session_id': Required['str'],
    'connectors': Required['builtins.list[str]'],
    'reconnect': 'bool',
}, total=False)

ConnectorsConnectResult = TypedDict('ConnectorsConnectResult', {
    'op_id': Required['str'],
    'seq': Required['int'],
    'deadline_at': Required['float'],
    'settled': Required['bool'],
    'settled_at': 'Union[float, None]',
    'settled_by': 'Union[ConnectionSettleReason, None]',
    'targets': Required['builtins.list[ConnectionOperationTarget]'],
    'status': 'Union[str, None]',
    'note': 'Union[str, None]',
}, total=False)

ConnectorsListParams = TypedDict('ConnectorsListParams', {
    'profile': 'Union[str, None]',
    'session_id': Required['str'],
}, total=False)

ConnectorsListResult = TypedDict('ConnectorsListResult', {
    'available': Required['bool'],
    'connectors': Required['builtins.list[ConnectorRow]'],
}, total=False)

ContextCategory = TypedDict('ContextCategory', {
    'color': Required['str'],
    'id': Required['str'],
    'label': Required['str'],
    'tokens': Required['int'],
}, total=False)

ContextFileSource = TypedDict('ContextFileSource', {
    'label': Required['str'],
    'path': Required['str'],
    'chars': Required['int'],
    'est_tokens': Required['int'],
    'loaded': Required['bool'],
    'status': Required['str'],
}, total=False)

ControllerScope = TypedDict('ControllerScope', {
    'principal_id': Required['str'],
    'profile_id': Required['str'],
    'session_id': Required['str'],
    'controller_id': Required['str'],
    'browser_profile_id': Required['str'],
    'transport_family': Required['str'],
    'capabilities': Required['builtins.list[str]'],
}, total=False)

CronJobRow = TypedDict('CronJobRow', {
    'job_id': Required['str'],
    'name': 'str',
    'skill': 'Union[str, None]',
    'skills': 'builtins.list[str]',
    'prompt_preview': 'str',
    'model': 'Union[str, None]',
    'provider': 'Union[str, None]',
    'base_url': 'Union[str, None]',
    'schedule': 'str',
    'repeat': 'Union[int, str, None]',
    'deliver': 'Union[str, None]',
    'next_run_at': 'Union[str, None]',
    'last_run_at': 'Union[str, None]',
    'last_status': 'Union[str, None]',
    'last_delivery_error': 'Union[str, None]',
    'last_delivery_unverified': 'Union[bool, None]',
    'last_fire_error': 'Union[str, None]',
    'last_error': 'Union[str, None]',
    'enabled': 'bool',
    'state': 'Union[str, None]',
    'paused_at': 'Union[str, None]',
    'paused_reason': 'Union[str, None]',
    'workdir': 'Union[str, None]',
    'script': 'Union[str, None]',
    'reasoning_effort': 'Union[str, None]',
    'monitor_script': 'Union[str, None]',
    'monitor_url': 'Union[str, None]',
    'monitor_state': 'Union[Any, None]',
    'no_agent': 'Union[bool, None]',
    'enabled_toolsets': 'Union[builtins.list[str], None]',
    'continuity': 'Union[bool, None]',
    'context_from': 'Union[builtins.list[str], None]',
    'attach_to_session': 'Union[bool, None]',
}, total=False)

CronManageParams = TypedDict('CronManageParams', {
    'action': 'CronAction',
    'name': 'Union[str, None]',
    'include_disabled': 'Union[bool, str, None]',
    'schedule': 'Union[str, None]',
    'prompt': 'Union[str, None]',
    'repeat': 'Union[int, str, None]',
    'continuity': 'Union[bool, str, None]',
    'deliver': 'Union[str, None]',
    'profile': 'Union[str, None]',
}, total=False)

CronManageResult = TypedDict('CronManageResult', {
    'success': 'Union[bool, None]',
    'error': 'Union[str, None]',
    'count': 'Union[int, None]',
    'jobs': 'Union[builtins.list[CronJobRow], None]',
    'scoped': 'Union[str, None]',
    'gateway_running': 'Union[bool, None]',
    'warning': 'Union[str, None]',
    'job_id': 'Union[str, None]',
    'name': 'Union[str, None]',
    'skill': 'Union[str, None]',
    'skills': 'Union[builtins.list[str], None]',
    'schedule': 'Union[str, None]',
    'repeat': 'Union[int, str, None]',
    'deliver': 'Union[str, None]',
    'next_run_at': 'Union[str, None]',
    'job': 'Union[CronJobRow, None]',
    'message': 'Union[str, None]',
    'guidance': 'Union[Any, None]',
    'removed_job': 'Union[CronRemovedJob, None]',
}, total=False)

CronRemovedJob = TypedDict('CronRemovedJob', {
    'id': Required['str'],
    'name': 'str',
    'schedule': 'Union[str, None]',
}, total=False)

CurrentSubscription = TypedDict('CurrentSubscription', {
    'tier_id': 'Union[str, None]',
    'tier_name': 'Union[str, None]',
    'monthly_credits': 'Union[str, None]',
    'credits_remaining': 'Union[str, None]',
    'cycle_ends_at': 'Union[str, None]',
    'pending_downgrade_tier_name': 'Union[str, None]',
    'pending_downgrade_at': 'Union[str, None]',
    'pending_downgrade_display': 'Union[str, None]',
    'cancel_at_period_end': Required['bool'],
    'cancellation_effective_at': 'Union[str, None]',
    'cancellation_effective_display': 'Union[str, None]',
}, total=False)

DelegationPauseParams = TypedDict('DelegationPauseParams', {
    'profile': 'Union[str, None]',
    'paused': 'bool',
}, total=False)

DelegationPauseResult = TypedDict('DelegationPauseResult', {
    'paused': Required['bool'],
}, total=False)

DelegationStatusResult = TypedDict('DelegationStatusResult', {
    'active': Required['builtins.list[ActiveSubagent]'],
    'paused': Required['bool'],
    'max_spawn_depth': Required['int'],
    'max_concurrent_children': Required['int'],
}, total=False)

DiagnosticsShareNousParams = TypedDict('DiagnosticsShareNousParams', {
    'error_context': 'Union[str, None]',
    'extra_files': 'Union[dict[str, str], None]',
    'log_lines': 'Union[int, None]',
}, total=False)

DiagnosticsShareNousResult = TypedDict('DiagnosticsShareNousResult', {
    'ok': Required['bool'],
    'view_url': 'Union[str, None]',
    'upload_id': 'Union[str, None]',
    'expires_at': 'Union[str, None]',
    'error': 'Union[str, None]',
}, total=False)

DiscoveredRepo = TypedDict('DiscoveredRepo', {
    'root': Required['str'],
    'label': 'str',
    'sessions': 'int',
    'last_active': 'float',
}, total=False)

EmptyRequestParams = TypedDict('EmptyRequestParams', {
    'session_id': Required['str'],
}, total=False)

ErrorPayload = TypedDict('ErrorPayload', {
    'message': Required['str'],
}, total=False)

ErrorSurface = TypedDict('ErrorSurface', {
    'layer': Required['str'],
    'code': Required['str'],
    'retryable': Required['bool'],
    'provider': 'Union[str, None]',
    'model': 'Union[str, None]',
    'resets_at': 'Union[float, None]',
}, total=False)

FileAttachParams = TypedDict('FileAttachParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'path': 'Union[str, None]',
    'data_url': 'Union[str, None]',
    'name': 'Union[str, None]',
}, total=False)

FileAttachResult = TypedDict('FileAttachResult', {
    'attached': Required['bool'],
    'name': Required['str'],
    'path': Required['str'],
    'ref_path': Required['str'],
    'ref_text': Required['str'],
    'uploaded': Required['bool'],
}, total=False)

ForeignSessionRow = TypedDict('ForeignSessionRow', {
    'id': Required['str'],
    'source': Required['ForeignSource'],
    'label': Required['str'],
    'title': 'str',
    'cwd': 'Union[str, None]',
    'mtime': Required['float'],
    'turn_count': 'int',
    'excerpt': 'str',
}, total=False)

ForeignTurn = TypedDict('ForeignTurn', {
    'role': Required['str'],
    'content': Required['str'],
}, total=False)

FreeTierAckNoticeResult = TypedDict('FreeTierAckNoticeResult', {
    'acked': Required['bool'],
}, total=False)

FreeTierProvisionResult = TypedDict('FreeTierProvisionResult', {
    'has_guest': Required['bool'],
    'enabled': Required['bool'],
    'error': 'Union[str, None]',
}, total=False)

FreeTierStatusResult = TypedDict('FreeTierStatusResult', {
    'has_guest': Required['bool'],
    'enabled': Required['bool'],
    'available': Required['bool'],
    'notice_pending': Required['bool'],
    'model': Required['str'],
    'label': Required['str'],
}, total=False)

GatewayCapabilitiesResult = TypedDict('GatewayCapabilitiesResult', {
    'per_session_exclusive_submit': Required['bool'],
}, total=False)

GatewayReadyPayload = TypedDict('GatewayReadyPayload', {
    'skin': Required['SkinPayload'],
    'change_events': Required['bool'],
    'replay_epoch': Required['str'],
    'heartbeat': 'Union[bool, None]',
}, total=False)

GoalContractSnapshot = TypedDict('GoalContractSnapshot', {
    'outcome': 'str',
    'verification': 'str',
    'constraints': 'str',
    'boundaries': 'str',
    'stop_when': 'str',
}, total=False)

GoalGateSnapshot = TypedDict('GoalGateSnapshot', {
    'command': Required['str'],
    'timeout_seconds': Required['int'],
    'max_retries': Required['int'],
    'attempts': Required['int'],
    'last_exit_code': 'Union[int, None]',
}, total=False)

GoalSnapshot = TypedDict('GoalSnapshot', {
    'title': Required['str'],
    'status': Required['str'],
    'turns_used': Required['int'],
    'max_turns': Required['int'],
    'contract': Required['GoalContractSnapshot'],
    'subgoals': Required['builtins.list[str]'],
    'gates': Required['builtins.list[GoalGateSnapshot]'],
    'created_at': 'Union[float, None]',
    'updated_at': 'Union[float, None]',
    'paused_reason': 'Union[str, None]',
    'last_verdict': 'Union[str, None]',
    'last_reason': 'Union[str, None]',
    'wait_barrier': 'Union[Union[WaitBarrierUntil, WaitBarrierTarget], None]',
}, total=False)

GroupsApproveParams = TypedDict('GroupsApproveParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'member_id': Required['str'],
    'task_id': Required['str'],
    'execution_generation': Required['int'],
    'choice': Required['ApprovalChoice'],
    'request_id': Required['str'],
}, total=False)

GroupsApproveResult = TypedDict('GroupsApproveResult', {
    'approved': 'bool',
    'result': Required['dict[str, Any]'],
}, total=False)

GroupsCapabilitiesParams = TypedDict('GroupsCapabilitiesParams', {
    'profile': 'Union[str, None]',
}, total=False)

GroupsCapabilitiesResult = TypedDict('GroupsCapabilitiesResult', {
    'protocol_version': Required['int'],
    'driver': Required['bool'],
    'persistent_process': Required['bool'],
    'authority_gateway_id': Required['str'],
    'room_link': Required['RoomLinkStatus'],
    'features': Required['builtins.list[str]'],
    'methods': Required['builtins.list[str]'],
    'max_log_limit': Required['int'],
}, total=False)

GroupsCreateParams = TypedDict('GroupsCreateParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'name': Required['str'],
    'members': Required['builtins.list[RoomMemberInput]'],
    'authority_gateway_id': 'Union[str, None]',
}, total=False)

GroupsCreateResult = TypedDict('GroupsCreateResult', {
    'room': Required['Room'],
}, total=False)

GroupsDemoteParams = TypedDict('GroupsDemoteParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'observed_gateway_id': Required['str'],
    'observed_epoch': Required['int'],
}, total=False)

GroupsDemoteResult = TypedDict('GroupsDemoteResult', {
    'room_id': Required['str'],
    'authority_gateway_id': Required['str'],
    'authority_epoch': Required['int'],
    'idempotent': Required['bool'],
}, total=False)

GroupsDisbandParams = TypedDict('GroupsDisbandParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'cancel_id': 'Union[str, None]',
}, total=False)

GroupsDisbandResult = TypedDict('GroupsDisbandResult', {
    'tombstone': Required['RoomTombstone'],
}, total=False)

GroupsListParams = TypedDict('GroupsListParams', {
    'profile': 'Union[str, None]',
    'include_disbanded': 'Union[bool, None]',
    'limit': 'Union[int, None]',
    'offset': 'Union[int, None]',
}, total=False)

GroupsListResult = TypedDict('GroupsListResult', {
    'rooms': Required['builtins.list[Room]'],
    'next_offset': 'Union[int, None]',
}, total=False)

GroupsLogParams = TypedDict('GroupsLogParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'since_seq': 'Union[int, None]',
    'limit': 'Union[int, None]',
    'include_disbanded': 'Union[bool, None]',
}, total=False)

GroupsLogResult = TypedDict('GroupsLogResult', {
    'events': Required['builtins.list[RoomEvent]'],
    'cursor': Required['int'],
    'latest_seq': Required['int'],
    'has_more': Required['bool'],
    'authority': Required['RoomAuthority'],
}, total=False)

GroupsPeerInviteParams = TypedDict('GroupsPeerInviteParams', {
    'profile': 'Union[str, None]',
    'room_id': 'Union[str, None]',
    'home_install_id': 'Union[str, None]',
    'authority_gateway_id': 'Union[str, None]',
    'authority_epoch': 'Union[int, None]',
    'member_id': 'Union[str, None]',
    'grant_id': 'Union[str, None]',
    'ttl_seconds': 'Union[float, None]',
}, total=False)

GroupsPeerInviteResult = TypedDict('GroupsPeerInviteResult', {
    'grant': Required['str'],
    'target_profile': Required['str'],
    'catalog': Required['RoomLinkCatalog'],
    'endpoint': Required['RoomLinkEndpoint'],
}, total=False)

GroupsPeerRegisterParams = TypedDict('GroupsPeerRegisterParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'member_id': Required['str'],
    'target_url': Required['str'],
    'target_profile': Required['str'],
    'grant': Required['str'],
    'catalog': Required['dict[str, Any]'],
    'cancellation_scope_id': 'Union[str, None]',
    'trace_id': 'Union[str, None]',
}, total=False)

GroupsPeerRegisterResult = TypedDict('GroupsPeerRegisterResult', {
    'registered': 'bool',
    'mode': Required['str'],
    'transport_security': Required['str'],
    'target_install_id': Required['str'],
    'target_profile': Required['str'],
}, total=False)

GroupsPeerRevokeParams = TypedDict('GroupsPeerRevokeParams', {
    'profile': 'Union[str, None]',
    'grant': Required['str'],
}, total=False)

GroupsPeerRevokeResult = TypedDict('GroupsPeerRevokeResult', {
    'revoked': 'bool',
}, total=False)

GroupsPromoteParams = TypedDict('GroupsPromoteParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'confirm': 'Union[bool, None]',
    'reason': 'Union[str, None]',
}, total=False)

GroupsPromoteResult = TypedDict('GroupsPromoteResult', {
    'room_id': Required['str'],
    'authority_gateway_id': Required['str'],
    'authority_epoch': Required['int'],
    'previous_gateway_id': Required['str'],
    'previous_epoch': Required['int'],
    'claim_seq': Required['int'],
    'latest_seq': Required['int'],
}, total=False)

GroupsRenameParams = TypedDict('GroupsRenameParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'event_id': Required['str'],
    'name': Required['str'],
}, total=False)

GroupsRenameResult = TypedDict('GroupsRenameResult', {
    'room': Required['Room'],
}, total=False)

GroupsReplicaStateParams = TypedDict('GroupsReplicaStateParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
}, total=False)

GroupsReplicaStateResult = TypedDict('GroupsReplicaStateResult', {
    'room_id': Required['str'],
    'name': Required['str'],
    'members': Required['builtins.list[RoomMember]'],
    'authority': Required['RoomAuthority'],
    'last_seq': Required['int'],
    'latest_seq': Required['int'],
    'event_bytes': Required['int'],
    'created_at': Required['float'],
    'updated_at': Required['float'],
}, total=False)

GroupsReplicateParams = TypedDict('GroupsReplicateParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'room_name': Required['str'],
    'members': Required['builtins.list[RoomMemberInput]'],
    'page': Required['dict[str, Any]'],
}, total=False)

GroupsReplicateResult = TypedDict('GroupsReplicateResult', {
    'room_id': Required['str'],
    'stored_seq': Required['int'],
    'ingested': Required['int'],
    'authority': Required['RoomAuthority'],
    'caught_up': Required['bool'],
}, total=False)

GroupsRetryParams = TypedDict('GroupsRetryParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'task_id': Required['str'],
}, total=False)

GroupsRetryResult = TypedDict('GroupsRetryResult', {
    'retried': 'bool',
    'task': Required['RoomTaskReceipt'],
}, total=False)

GroupsSendParams = TypedDict('GroupsSendParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'event_id': 'Union[str, None]',
    'payload': Required['dict[str, Any]'],
}, total=False)

GroupsSendResult = TypedDict('GroupsSendResult', {
    'event': Required['RoomEvent'],
    'client_event_id': 'Union[str, None]',
    'accepted': 'bool',
    'driver_started': 'bool',
}, total=False)

GroupsStateParams = TypedDict('GroupsStateParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'include_disbanded': 'Union[bool, None]',
}, total=False)

GroupsStateResult = TypedDict('GroupsStateResult', {
    'room': Required['Room'],
    'driver_status': 'Union[RoomDriverStatus, None]',
}, total=False)

GroupsStopParams = TypedDict('GroupsStopParams', {
    'profile': 'Union[str, None]',
    'room_id': Required['str'],
    'cancel_id': 'Union[str, None]',
}, total=False)

GroupsStopResult = TypedDict('GroupsStopResult', {
    'cancelled': Required['int'],
}, total=False)

HandoffFailParams = TypedDict('HandoffFailParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'error': 'Union[str, None]',
}, total=False)

HandoffFailResult = TypedDict('HandoffFailResult', {
    'failed': Required['bool'],
    'state': Required['str'],
}, total=False)

HandoffRequestParams = TypedDict('HandoffRequestParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'platform': Required['str'],
}, total=False)

HandoffRequestResult = TypedDict('HandoffRequestResult', {
    'queued': Required['bool'],
    'session_key': Required['str'],
    'platform': Required['str'],
    'home_name': Required['str'],
}, total=False)

HandoffStateResult = TypedDict('HandoffStateResult', {
    'state': Required['str'],
    'platform': Required['str'],
    'error': Required['str'],
}, total=False)

HeartbeatSnapshot = TypedDict('HeartbeatSnapshot', {
    'prompt': Required['str'],
    'status': Required['str'],
    'interval_seconds': Required['int'],
    'created_at': Required['float'],
    'last_fired_at': Required['float'],
    'fire_count': Required['int'],
}, total=False)

ImageAttachBytesParams = TypedDict('ImageAttachBytesParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'content_base64': 'Union[str, None]',
    'data': 'Union[str, None]',
    'filename': 'Union[str, None]',
    'ext': 'Union[str, None]',
}, total=False)

ImageAttachParams = TypedDict('ImageAttachParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'path': Required['str'],
}, total=False)

ImageDetachParams = TypedDict('ImageDetachParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'path': Required['str'],
}, total=False)

ImageDetachResult = TypedDict('ImageDetachResult', {
    'detached': Required['bool'],
    'count': Required['int'],
}, total=False)

ImageGenerateParams = TypedDict('ImageGenerateParams', {
    'prompt': 'Union[str, None]',
    'aspect_ratio': 'Union[str, None]',
    'probe': 'Union[Any, None]',
    'max_bytes': 'Union[int, None]',
}, total=False)

ImageGenerateResult = TypedDict('ImageGenerateResult', {
    'available': Required['bool'],
    'success': 'Union[bool, None]',
    'image': 'Union[str, None]',
    'image_data': 'Union[str, None]',
    'error': 'Union[str, None]',
}, total=False)

InflightTurn = TypedDict('InflightTurn', {
    'assistant': 'str',
    'streaming': 'bool',
    'user': 'str',
    'display_kind': 'Union[str, None]',
    'display_metadata': 'Union[dict[str, Any], None]',
    'corrections': 'Union[builtins.list[str], None]',
    'correction_offsets': 'Union[builtins.list[int], None]',
    'error': 'Union[str, None]',
    'status': 'Union[str, None]',
    'recoverable': 'Union[bool, None]',
    'error_surface': 'Union[dict[str, Any], None]',
}, total=False)

InputDetectDropParams = TypedDict('InputDetectDropParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'text': 'Union[str, None]',
}, total=False)

InputDetectDropResult = TypedDict('InputDetectDropResult', {
    'name': 'Union[str, None]',
    'width': 'Union[int, None]',
    'height': 'Union[int, None]',
    'token_estimate': 'Union[int, None]',
    'matched': Required['bool'],
    'is_image': 'Union[bool, None]',
    'path': 'Union[str, None]',
    'count': 'Union[int, None]',
    'text': 'Union[str, None]',
}, total=False)

InsightsGetParams = TypedDict('InsightsGetParams', {
    'days': 'Union[int, None]',
    'profile': 'Union[str, None]',
}, total=False)

InsightsGetResult = TypedDict('InsightsGetResult', {
    'days': Required['int'],
    'sessions': Required['int'],
    'messages': Required['int'],
}, total=False)

LayoutApplyPayload = TypedDict('LayoutApplyPayload', {
    'preset': Required['str'],
}, total=False)

LearningAxis = TypedDict('LearningAxis', {
    'start': Required['str'],
    'end': Required['str'],
}, total=False)

LearningBucketRow = TypedDict('LearningBucketRow', {
    'index': Required['int'],
    'label': Required['str'],
    'date': Required['str'],
    'skills': Required['int'],
    'memories': Required['int'],
    'total': Required['int'],
    'category': 'Union[str, None]',
    'color': 'Union[str, None]',
    'nodes': Required['builtins.list[LearningNodeRow]'],
}, total=False)

LearningDetailResult = TypedDict('LearningDetailResult', {
    'ok': Required['bool'],
    'message': 'Union[str, None]',
    'kind': 'Union[str, None]',
    'id': 'Union[str, None]',
    'label': 'Union[str, None]',
    'content': 'Union[str, None]',
}, total=False)

LearningEditParams = TypedDict('LearningEditParams', {
    'id': 'Union[str, None]',
    'content': 'Union[str, None]',
}, total=False)

LearningFrame = TypedDict('LearningFrame', {
    'reveal': Required['float'],
    'date': Required['str'],
    'visible': Required['int'],
    'grid': Required['builtins.list[builtins.list[Any]]'],
    'labels': 'builtins.list[dict[str, Any]]',
}, total=False)

LearningFramesParams = TypedDict('LearningFramesParams', {
    'cols': 'Union[int, None]',
    'rows': 'Union[int, None]',
    'frames': 'Union[int, None]',
}, total=False)

LearningFramesResult = TypedDict('LearningFramesResult', {
    'frames': Required['builtins.list[LearningFrame]'],
    'legend': Required['builtins.list[LearningLegendItem]'],
    'categories': Required['builtins.list[LearningLegendItem]'],
    'buckets': Required['builtins.list[LearningBucketRow]'],
    'summary': Required['builtins.list[str]'],
    'axis': Required['LearningAxis'],
    'count': Required['int'],
    'cols': Required['int'],
    'rows': Required['int'],
}, total=False)

LearningLegendItem = TypedDict('LearningLegendItem', {
    'glyph': Required['str'],
    'label': Required['str'],
    'style': 'Union[str, None]',
    'color': 'Union[str, None]',
}, total=False)

LearningMutationResult = TypedDict('LearningMutationResult', {
    'ok': Required['bool'],
    'message': 'Union[str, None]',
}, total=False)

LearningNodeParams = TypedDict('LearningNodeParams', {
    'id': 'Union[str, None]',
}, total=False)

LearningNodeRow = TypedDict('LearningNodeRow', {
    'id': Required['str'],
    'glyph': Required['str'],
    'label': Required['str'],
    'fullLabel': Required['str'],
    'meta': Required['str'],
    'body': Required['str'],
    'style': Required['str'],
}, total=False)

LegacyPluginRow = TypedDict('LegacyPluginRow', {
    'name': Required['str'],
    'version': Required['str'],
    'enabled': Required['bool'],
}, total=False)

LlmOneshotParams = TypedDict('LlmOneshotParams', {
    'profile': 'Union[str, None]',
    'template': 'Union[str, None]',
    'instructions': 'Union[str, None]',
    'input': 'Union[str, None]',
    'variables': 'Union[dict[str, Any], None]',
    'task': 'Union[str, None]',
    'temperature': 'Union[float, None]',
    'max_tokens': 'Union[int, None]',
    'session_id': 'Union[str, None]',
}, total=False)

LlmOneshotResult = TypedDict('LlmOneshotResult', {
    'text': Required['str'],
}, total=False)

LoopSnapshot = TypedDict('LoopSnapshot', {
    'prompt': Required['str'],
    'status': Required['str'],
    'mode': Required['str'],
    'interval_seconds': Required['float'],
    'current_delay': Required['float'],
    'times': Required['int'],
    'until': Required['str'],
    'max_ticks': Required['int'],
    'ticks_fired': Required['int'],
    'created_at': Required['float'],
    'last_fired_at': Required['float'],
    'next_due_at': Required['float'],
    'awaiting_response': Required['bool'],
    'deferred_by_goal': Required['bool'],
    'paused_reason': 'Union[str, None]',
    'last_stop_reason': 'Union[str, None]',
}, total=False)

McpCatalogEntry = TypedDict('McpCatalogEntry', {
    'name': Required['str'],
    'description': Required['str'],
    'installed': Required['bool'],
    'enabled': Required['bool'],
    'requires': Required['builtins.list[str]'],
    'transport': Required['str'],
}, total=False)

McpCatalogResult = TypedDict('McpCatalogResult', {
    'servers': Required['builtins.list[McpCatalogEntry]'],
}, total=False)

McpOauthCallbackParams = TypedDict('McpOauthCallbackParams', {
    'profile': 'Union[str, None]',
    'name': Required['str'],
    'session_id': Required['str'],
    'code': 'Union[str, None]',
    'state': 'Union[str, None]',
    'error': 'Union[str, None]',
    'iss': 'Union[str, None]',
}, total=False)

McpOauthCallbackResult = TypedDict('McpOauthCallbackResult', {
    'ok': Required['bool'],
    'session_id': 'Union[str, None]',
    'error_message': 'Union[str, None]',
}, total=False)

McpOauthCancelResult = TypedDict('McpOauthCancelResult', {
    'ok': Required['bool'],
    'status': 'Union[str, None]',
    'error_message': 'Union[str, None]',
}, total=False)

McpOauthFlowParams = TypedDict('McpOauthFlowParams', {
    'profile': 'Union[str, None]',
    'name': Required['str'],
    'session_id': Required['str'],
}, total=False)

McpOauthPollResult = TypedDict('McpOauthPollResult', {
    'ok': Required['bool'],
    'status': Required['McpOauthPollStatus'],
    'session_id': 'Union[str, None]',
    'error_message': 'Union[str, None]',
    'auth_url': 'Union[str, None]',
    'tools': 'Union[builtins.list[McpProbeTool], None]',
}, total=False)

McpOauthStartParams = TypedDict('McpOauthStartParams', {
    'profile': 'Union[str, None]',
    'name': Required['str'],
    'client_redirect_uri': 'Union[str, None]',
}, total=False)

McpOauthStartResult = TypedDict('McpOauthStartResult', {
    'ok': Required['bool'],
    'session_id': Required['str'],
    'auth_url': Required['str'],
    'flow': Required['str'],
}, total=False)

McpProbeTool = TypedDict('McpProbeTool', {
    'name': Required['str'],
    'description': Required['str'],
}, total=False)

McpServerEntry = TypedDict('McpServerEntry', {
    'name': Required['str'],
    'enabled': 'bool',
    'transport': 'str',
}, total=False)

McpServerNameParams = TypedDict('McpServerNameParams', {
    'profile': 'Union[str, None]',
    'name': Required['str'],
}, total=False)

McpServerRuntimeRow = TypedDict('McpServerRuntimeRow', {
    'name': Required['str'],
    'transport': Required['str'],
    'tools': Required['int'],
    'connected': Required['bool'],
    'disabled': Required['bool'],
    'status': Required['McpRuntimeStatus'],
}, total=False)

McpServerStatus = TypedDict('McpServerStatus', {
    'name': 'str',
    'status': 'Union[str, None]',
    'tool_count': 'Union[int, None]',
    'error': 'Union[str, None]',
}, total=False)

McpServerSummary = TypedDict('McpServerSummary', {
    'name': Required['str'],
    'transport': Required['str'],
    'url': 'Union[str, None]',
    'command': 'Union[str, None]',
    'args': Required['builtins.list[str]'],
    'env': Required['builtins.list[str]'],
    'auth': 'Union[str, None]',
    'oauth_tokens_present': 'Union[bool, None]',
    'enabled': Required['bool'],
    'tools': 'Union[Any, None]',
}, total=False)

McpServersAddParams = TypedDict('McpServersAddParams', {
    'profile': 'Union[str, None]',
    'name': Required['str'],
    'preset': 'Union[str, None]',
    'config': 'Union[dict[str, Any], None]',
    'bearer_token': 'Union[str, None]',
}, total=False)

McpServersAddResult = TypedDict('McpServersAddResult', {
    'ok': Required['bool'],
    'name': Required['str'],
    'server': Required['McpServerSummary'],
}, total=False)

McpServersListResult = TypedDict('McpServersListResult', {
    'servers': Required['builtins.list[McpServerSummary]'],
}, total=False)

McpServersRemoveResult = TypedDict('McpServersRemoveResult', {
    'ok': Required['bool'],
    'removed': Required['bool'],
}, total=False)

McpServersSetApiKeyParams = TypedDict('McpServersSetApiKeyParams', {
    'profile': 'Union[str, None]',
    'name': Required['str'],
    'value': Required['str'],
    'env_var': 'Union[str, None]',
}, total=False)

McpServersSetApiKeyResult = TypedDict('McpServersSetApiKeyResult', {
    'ok': Required['bool'],
    'name': Required['str'],
    'env_var': Required['str'],
    'server': Required['McpServerSummary'],
}, total=False)

McpServersStatusResult = TypedDict('McpServersStatusResult', {
    'servers': Required['builtins.list[McpServerRuntimeRow]'],
    'checked_at': Required['int'],
}, total=False)

McpServersTestResult = TypedDict('McpServersTestResult', {
    'ok': Required['bool'],
    'tools': Required['builtins.list[McpProbeTool]'],
    'error': 'Union[str, None]',
    'prompts': 'Union[int, None]',
    'resources': 'Union[int, None]',
    'oauth_needed': Required['bool'],
    'oauth_tokens_present': 'Union[bool, None]',
}, total=False)

MessageCompletePayload = TypedDict('MessageCompletePayload', {
    'text': 'Union[str, Any]',
    'usage': 'Union[Usage, None]',
    'status': 'Union[TurnStatus, None]',
    'reasoning': 'Union[str, None]',
    'warning': 'Union[str, None]',
    'response_previewed': 'Union[bool, None]',
    'billing': 'Union[BillingBlock, None]',
    'failure_reason': 'Union[str, None]',
    'rendered': 'Union[str, None]',
    'error': 'Union[str, None]',
    'recoverable': 'Union[bool, None]',
    'error_surface': 'Union[ErrorSurface, None]',
    'partial': 'Union[bool, None]',
}, total=False)

MessageInterimPayload = TypedDict('MessageInterimPayload', {
    'text': Required['str'],
    'already_streamed': Required['bool'],
}, total=False)

MessageReactParams = TypedDict('MessageReactParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'row_id': 'Union[int, None]',
    'newest_role': 'Union[str, None]',
    'emoji': 'Union[str, None]',
    'author': 'Union[ReactionAuthor, None]',
}, total=False)

MessageReactResult = TypedDict('MessageReactResult', {
    'row_id': Required['int'],
    'reactions': Required['builtins.list[MessageReaction]'],
}, total=False)

MessageReaction = TypedDict('MessageReaction', {
    'emoji': Required['str'],
    'author': Required['str'],
    'at': 'Union[float, None]',
    'seen': 'Union[bool, None]',
}, total=False)

MessageReactionPayload = TypedDict('MessageReactionPayload', {
    'row_id': Required['int'],
    'reactions': Required['builtins.list[MessageReaction]'],
    'role': Required['str'],
}, total=False)

MoaAggregatingPayload = TypedDict('MoaAggregatingPayload', {
    'aggregator': Required['str'],
}, total=False)

MoaPhasePayload = TypedDict('MoaPhasePayload', {
    'phase': Required['str'],
    'refs_done': 'Union[int, None]',
    'refs_total': 'Union[int, None]',
    'aggregator': 'Union[str, None]',
}, total=False)

MoaProgressPayload = TypedDict('MoaProgressPayload', {
    'label': Required['str'],
    'refs_done': Required['int'],
    'refs_total': Required['int'],
}, total=False)

MoaReferencePayload = TypedDict('MoaReferencePayload', {
    'label': Required['str'],
    'text': Required['str'],
    'index': 'Union[int, None]',
    'count': 'Union[int, None]',
}, total=False)

ModelCapabilities = TypedDict('ModelCapabilities', {
    'fast': Required['bool'],
    'reasoning': Required['bool'],
    'can_disable_reasoning': 'Union[bool, None]',
}, total=False)

ModelDisconnectParams = TypedDict('ModelDisconnectParams', {
    'slug': Required['str'],
    'session_id': 'Union[str, None]',
}, total=False)

ModelDisconnectResult = TypedDict('ModelDisconnectResult', {
    'slug': Required['str'],
    'name': Required['str'],
    'disconnected': Required['bool'],
}, total=False)

ModelOptionProvider = TypedDict('ModelOptionProvider', {
    'slug': Required['str'],
    'name': Required['str'],
    'models': 'builtins.list[str]',
    'total_models': 'Union[int, None]',
    'is_current': 'Union[bool, None]',
    'is_user_defined': 'Union[bool, None]',
    'source': 'Union[str, None]',
    'aliases': 'Union[builtins.list[str], None]',
    'api_url': 'Union[str, None]',
    'auth_type': 'Union[str, None]',
    'authenticated': 'Union[bool, None]',
    'key_env': 'Union[str, None]',
    'warning': 'Union[str, None]',
    'featured_models': 'Union[builtins.list[str], None]',
    'capabilities': 'Union[dict[str, ModelCapabilities], None]',
    'pricing': 'Union[dict[str, ModelPricing], None]',
    'pricing_pending': 'Union[bool, None]',
    'free_tier': 'Union[bool, None]',
    'free_tier_pending': 'Union[bool, None]',
    'free_tier_row': 'Union[bool, None]',
    'unavailable_models': 'Union[builtins.list[str], None]',
}, total=False)

ModelOptionsParams = TypedDict('ModelOptionsParams', {
    'profile': 'Union[str, None]',
    'session_id': 'Union[str, None]',
    'explicit_only': 'bool',
    'include_unconfigured': 'bool',
    'refresh': 'bool',
}, total=False)

ModelOptionsResult = TypedDict('ModelOptionsResult', {
    'providers': Required['builtins.list[ModelOptionProvider]'],
    'model': 'str',
    'provider': 'str',
}, total=False)

ModelPricing = TypedDict('ModelPricing', {
    'input': Required['str'],
    'output': Required['str'],
    'cache': 'Union[str, None]',
    'free': Required['bool'],
    'discount_percent': 'Union[int, None]',
    'was_input': 'Union[str, None]',
    'was_output': 'Union[str, None]',
}, total=False)

ModelSaveKeyParams = TypedDict('ModelSaveKeyParams', {
    'slug': Required['str'],
    'api_key': Required['str'],
    'session_id': 'Union[str, None]',
}, total=False)

ModelSaveKeyResult = TypedDict('ModelSaveKeyResult', {
    'provider': Required['ModelOptionProvider'],
}, total=False)

NoticePayload = TypedDict('NoticePayload', {
    'message': Required['str'],
}, total=False)

NotificationClearPayload = TypedDict('NotificationClearPayload', {
    'key': Required['str'],
}, total=False)

NotificationShowPayload = TypedDict('NotificationShowPayload', {
    'text': Required['str'],
    'level': Required['str'],
    'kind': Required['str'],
    'ttl_ms': 'Union[int, None]',
    'key': 'Union[str, None]',
    'id': 'Union[str, None]',
}, total=False)

OkResult = TypedDict('OkResult', {
    'ok': 'bool',
}, total=False)

OnboardingAnswers = TypedDict('OnboardingAnswers', {
    'name': 'Union[str, None]',
    'context': 'Union[str, None]',
    'theme': 'Union[str, None]',
    'accent': 'Union[str, None]',
    'layout': 'Union[str, None]',
    'focus': 'Union[builtins.list[str], None]',
    'connectors': 'Union[builtins.list[str], None]',
}, total=False)

OpenRequestEntry = TypedDict('OpenRequestEntry', {
    'id': Required['str'],
    'method': Required['str'],
    'params': Required['dict[str, Any]'],
}, total=False)

OptionalProjectResult = TypedDict('OptionalProjectResult', {
    'project': 'Union[ProjectInfo, None]',
}, total=False)

PaneRevealPayload = TypedDict('PaneRevealPayload', {
    'pane': Required['str'],
}, total=False)

PasteCollapseParams = TypedDict('PasteCollapseParams', {
    'text': 'Union[str, None]',
}, total=False)

PasteCollapseResult = TypedDict('PasteCollapseResult', {
    'placeholder': Required['str'],
    'path': Required['str'],
    'lines': Required['int'],
}, total=False)

PdfAttachParams = TypedDict('PdfAttachParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'path': 'Union[str, None]',
    'content_base64': 'Union[str, None]',
    'data': 'Union[str, None]',
    'filename': 'Union[str, None]',
    'first_page': 'Union[int, None]',
    'last_page': 'Union[int, None]',
}, total=False)

PdfAttachResult = TypedDict('PdfAttachResult', {
    'attached': Required['bool'],
    'filename': Required['str'],
    'pages_attached': Required['int'],
    'pages': Required['builtins.list[PdfPage]'],
    'count': Required['int'],
    'text': Required['str'],
}, total=False)

PdfPage = TypedDict('PdfPage', {
    'name': 'Union[str, None]',
    'width': 'Union[int, None]',
    'height': 'Union[int, None]',
    'token_estimate': 'Union[int, None]',
    'path': Required['str'],
    'page': Required['int'],
}, total=False)

PeerRouteStatus = TypedDict('PeerRouteStatus', {
    'room_id': Required['str'],
    'member_id': Required['str'],
    'status': Required['str'],
}, total=False)

PendingApproval = TypedDict('PendingApproval', {
    'request_id': 'Union[str, None]',
    'command': 'Union[str, None]',
    'description': 'Union[str, None]',
    'pattern_key': 'Union[str, None]',
    'pattern_keys': 'Union[builtins.list[str], None]',
    'allow_permanent': 'Union[bool, None]',
    'allow_session': 'Union[bool, None]',
    'smart_denied': 'Union[bool, None]',
    'choices': 'Union[builtins.list[str], None]',
    'tool_name': 'Union[str, None]',
}, total=False)

PetCancelParams = TypedDict('PetCancelParams', {
    'profile': 'Union[str, None]',
    'token': 'Union[str, None]',
}, total=False)

PetCancelResult = TypedDict('PetCancelResult', {
    'ok': Required['bool'],
}, total=False)

PetCellsParams = TypedDict('PetCellsParams', {
    'profile': 'Union[str, None]',
    'state': 'Union[str, None]',
    'cols': 'Union[int, None]',
    'graphics': 'bool',
}, total=False)

PetCellsResult = TypedDict('PetCellsResult', {
    'enabled': Required['bool'],
    'slug': 'Union[str, None]',
    'displayName': 'Union[str, None]',
    'state': 'Union[str, None]',
    'cols': 'Union[int, None]',
    'frameMs': 'Union[float, None]',
    'frames': 'Union[builtins.list[builtins.list[builtins.list[builtins.list[int]]]], builtins.list[str], None]',
    'scale': 'Union[float, None]',
    'graphics': 'Union[str, None]',
    'imageId': 'Union[int, None]',
    'color': 'Union[str, None]',
    'rows': 'Union[int, None]',
    'placeholder': 'Union[builtins.list[str], None]',
}, total=False)

PetChangedPayload = TypedDict('PetChangedPayload', {
    'enabled': Required['bool'],
    'slug': 'Union[str, None]',
    'displayName': 'Union[str, None]',
    'scale': 'Union[float, None]',
    'spritesheetRevision': 'Union[str, None]',
}, total=False)

PetDraft = TypedDict('PetDraft', {
    'index': Required['int'],
    'dataUri': Required['str'],
}, total=False)

PetExportResult = TypedDict('PetExportResult', {
    'ok': Required['bool'],
    'filename': Required['str'],
    'zipBase64': Required['str'],
}, total=False)

PetGalleryEntry = TypedDict('PetGalleryEntry', {
    'slug': Required['str'],
    'displayName': Required['str'],
    'installed': Required['bool'],
    'spritesheetUrl': 'str',
    'curated': 'Union[bool, None]',
    'generated': 'bool',
}, total=False)

PetGalleryParams = TypedDict('PetGalleryParams', {
    'profile': 'Union[str, None]',
    'localOnly': 'bool',
}, total=False)

PetGalleryResult = TypedDict('PetGalleryResult', {
    'enabled': Required['bool'],
    'active': 'str',
    'pets': 'builtins.list[PetGalleryEntry]',
}, total=False)

PetGenProvider = TypedDict('PetGenProvider', {
    'name': Required['str'],
    'label': Required['str'],
    'default': Required['bool'],
}, total=False)

PetGenerateParams = TypedDict('PetGenerateParams', {
    'profile': 'Union[str, None]',
    'prompt': 'Union[str, None]',
    'referenceImage': 'Union[str, None]',
    'count': 'Union[int, None]',
    'style': 'Union[str, None]',
    'provider': 'Union[str, None]',
}, total=False)

PetGenerateProgressPayload = TypedDict('PetGenerateProgressPayload', {
    'token': Required['str'],
    'count': Required['int'],
    'index': 'Union[int, None]',
    'dataUri': 'Union[str, None]',
}, total=False)

PetGenerateResult = TypedDict('PetGenerateResult', {
    'ok': Required['bool'],
    'token': Required['str'],
    'drafts': Required['builtins.list[PetDraft]'],
}, total=False)

PetGenerateStatusResult = TypedDict('PetGenerateStatusResult', {
    'available': Required['bool'],
    'providers': Required['builtins.list[PetGenProvider]'],
}, total=False)

PetHatchParams = TypedDict('PetHatchParams', {
    'profile': 'Union[str, None]',
    'token': Required['str'],
    'name': Required['str'],
    'cancelToken': 'Union[str, None]',
    'index': 'Union[int, None]',
    'description': 'Union[str, None]',
    'prompt': 'Union[str, None]',
    'style': 'Union[str, None]',
    'provider': 'Union[str, None]',
}, total=False)

PetHatchProgressPayload = TypedDict('PetHatchProgressPayload', {
    'event': Required['str'],
    'detail': 'Union[str, None]',
    'state': 'Union[str, None]',
    'done': 'Union[str, None]',
    'total': 'Union[str, None]',
}, total=False)

PetHatchResult = TypedDict('PetHatchResult', {
    'ok': Required['bool'],
    'slug': Required['str'],
    'displayName': Required['str'],
    'warnings': 'builtins.list[Any]',
    'pet': Required['PetSpritePayload'],
}, total=False)

PetInfoMetaResult = TypedDict('PetInfoMetaResult', {
    'enabled': Required['bool'],
    'slug': 'Union[str, None]',
    'displayName': 'Union[str, None]',
    'scale': 'Union[float, None]',
    'spritesheetRevision': 'Union[str, None]',
}, total=False)

PetInfoParams = TypedDict('PetInfoParams', {
    'profile': 'Union[str, None]',
    'knownRevision': 'Union[str, None]',
}, total=False)

PetInfoResult = TypedDict('PetInfoResult', {
    'enabled': Required['bool'],
    'slug': 'Union[str, None]',
    'displayName': 'Union[str, None]',
    'mime': 'Union[str, None]',
    'spritesheetBase64': 'Union[str, None]',
    'spritesheetRevision': 'Union[str, None]',
    'spritesheetUnchanged': 'Union[bool, None]',
    'frameW': 'Union[int, None]',
    'frameH': 'Union[int, None]',
    'framesPerState': 'Union[int, None]',
    'framesByState': 'Union[dict[str, int], None]',
    'framesByRow': 'Union[dict[str, int], None]',
    'loopMs': 'Union[int, None]',
    'scale': 'Union[float, None]',
    'stateRows': 'Union[builtins.list[str], None]',
}, total=False)

PetRenameParams = TypedDict('PetRenameParams', {
    'profile': 'Union[str, None]',
    'slug': Required['str'],
    'name': Required['str'],
}, total=False)

PetScaleParams = TypedDict('PetScaleParams', {
    'profile': 'Union[str, None]',
    'scale': 'Any',
}, total=False)

PetScaleResult = TypedDict('PetScaleResult', {
    'ok': Required['bool'],
    'scale': Required['float'],
}, total=False)

PetSlugParams = TypedDict('PetSlugParams', {
    'profile': 'Union[str, None]',
    'slug': Required['str'],
}, total=False)

PetSlugResult = TypedDict('PetSlugResult', {
    'ok': Required['bool'],
    'slug': Required['str'],
    'displayName': 'Union[str, None]',
}, total=False)

PetSpritePayload = TypedDict('PetSpritePayload', {
    'slug': 'Union[str, None]',
    'displayName': 'Union[str, None]',
    'mime': 'Union[str, None]',
    'spritesheetBase64': 'Union[str, None]',
    'spritesheetRevision': 'Union[str, None]',
    'frameW': 'Union[int, None]',
    'frameH': 'Union[int, None]',
    'framesPerState': 'Union[int, None]',
    'framesByState': 'Union[dict[str, int], None]',
    'framesByRow': 'Union[dict[str, int], None]',
    'loopMs': 'Union[int, None]',
    'scale': 'Union[float, None]',
    'stateRows': 'Union[builtins.list[str], None]',
}, total=False)

PetThumbParams = TypedDict('PetThumbParams', {
    'profile': 'Union[str, None]',
    'slug': Required['str'],
    'url': 'Union[str, None]',
}, total=False)

PetThumbResult = TypedDict('PetThumbResult', {
    'ok': Required['bool'],
    'slug': Required['str'],
    'dataUri': 'Union[str, None]',
}, total=False)

PingParams = TypedDict('PingParams', {

}, total=False)

PingResult = TypedDict('PingResult', {
    'pong': Required['bool'],
}, total=False)

PluginsListParams = TypedDict('PluginsListParams', {

}, total=False)

PluginsListResult = TypedDict('PluginsListResult', {
    'plugins': Required['builtins.list[LegacyPluginRow]'],
}, total=False)

PluginsManageParams = TypedDict('PluginsManageParams', {
    'profile': 'Union[str, None]',
    'action': 'PluginsAction',
    'key': 'Union[str, None]',
    'name': 'Union[str, None]',
    'enable': 'Union[bool, None]',
    'identifier': 'Union[str, None]',
    'repo': 'Union[str, None]',
    'catalog_name': 'Union[str, None]',
    'force': 'Union[bool, None]',
    'ref': 'Union[str, None]',
}, total=False)

PluginsManageResult = TypedDict('PluginsManageResult', {
    'plugins': 'Union[builtins.list[AgentPluginRow], None]',
    'user_count': 'Union[int, None]',
    'bundled_count': 'Union[int, None]',
    'ok': 'Union[bool, None]',
    'unchanged': 'Union[bool, None]',
    'name': 'Union[str, None]',
    'plugin': 'Union[AgentPluginRow, None]',
    'plugin_name': 'Union[str, None]',
    'warnings': 'Union[builtins.list[str], None]',
    'missing_env': 'Union[builtins.list[str], None]',
    'after_install_path': 'Union[str, None]',
    'enabled': 'Union[bool, None]',
    'sha': 'Union[str, None]',
}, total=False)

PreviewActRequestParams = TypedDict('PreviewActRequestParams', {
    'session_id': Required['str'],
    'action': Required['str'],
    'ref': 'Union[str, None]',
    'selector': 'Union[str, None]',
    'text': 'Union[str, None]',
    'key': 'Union[str, None]',
    'submit': 'Union[bool, None]',
    'full': 'Union[bool, None]',
    'to': 'Union[str, None]',
    'amount': 'Union[int, None]',
    'max': 'Union[int, None]',
}, total=False)

PreviewClosePayload = TypedDict('PreviewClosePayload', {
    'url': 'str',
}, total=False)

PreviewOpenPayload = TypedDict('PreviewOpenPayload', {
    'url': Required['str'],
    'label': 'str',
}, total=False)

PreviewRestartParams = TypedDict('PreviewRestartParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'url': Required['str'],
    'cwd': 'Union[str, None]',
    'context': 'Union[str, None]',
}, total=False)

PreviewRestartProgressPayload = TypedDict('PreviewRestartProgressPayload', {
    'task_id': Required['str'],
    'text': Required['str'],
    'level': 'Union[str, None]',
}, total=False)

ProcessEntry = TypedDict('ProcessEntry', {
    'session_id': Required['str'],
    'command': 'str',
    'cwd': 'Union[str, None]',
    'pid': 'Union[int, None]',
    'owner_task_id': 'Union[str, None]',
    'started_at': 'Union[str, None]',
    'uptime_seconds': 'Union[int, None]',
    'status': 'str',
    'output_preview': 'str',
    'output_tail': 'Union[str, None]',
    'session_scoped': 'Union[bool, None]',
    'watch_patterns': 'Union[builtins.list[str], None]',
    'watch_hit': 'Union[bool, None]',
    'notify_on_complete': 'Union[bool, None]',
    'exit_code': 'Union[int, None]',
    'exited_at': 'Union[float, None]',
    'completion_reason': 'Union[str, None]',
    'detached': 'Union[bool, None]',
}, total=False)

ProcessKillParams = TypedDict('ProcessKillParams', {
    'session_id': Required['str'],
    'process_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

ProcessKillResult = TypedDict('ProcessKillResult', {
    'status': Required['ProcessKillStatus'],
    'session_id': 'Union[str, None]',
    'command': 'Union[str, None]',
    'exit_code': 'Union[int, None]',
    'completion_reason': 'Union[str, None]',
    'termination_source': 'Union[str, None]',
    'output': 'Union[str, None]',
    'error': 'Union[str, None]',
}, total=False)

ProcessListParams = TypedDict('ProcessListParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

ProcessListResult = TypedDict('ProcessListResult', {
    'processes': 'builtins.list[ProcessEntry]',
}, total=False)

ProcessStopParams = TypedDict('ProcessStopParams', {
    'session_id': 'Union[str, None]',
    'profile': 'Union[str, None]',
}, total=False)

ProcessStopResult = TypedDict('ProcessStopResult', {
    'killed': Required['int'],
}, total=False)

ProfileCanonicalSession = TypedDict('ProfileCanonicalSession', {
    'id': Required['str'],
    'resolved_id': Required['str'],
    'root_title': 'str',
    'title': 'str',
    'preview': 'str',
    'started_at': 'Union[float, int]',
    'last_active': 'Union[float, int]',
    'message_count': 'int',
}, total=False)

ProfileMirrored = TypedDict('ProfileMirrored', {
    'env': 'bool',
    'auth': 'bool',
    'model_inherited': 'bool',
    'voice': 'bool',
}, total=False)

ProfileModelPin = TypedDict('ProfileModelPin', {
    'provider': 'str',
    'default': 'str',
}, total=False)

ProfileNameParams = TypedDict('ProfileNameParams', {
    'profile': 'Union[str, None]',
    'name': 'Union[str, None]',
}, total=False)

ProfileParams = TypedDict('ProfileParams', {
    'profile': 'Union[str, None]',
}, total=False)

ProfileRow = TypedDict('ProfileRow', {
    'name': Required['str'],
    'path': Required['str'],
    'is_default': 'bool',
    'model': 'Union[str, None]',
    'provider': 'Union[str, None]',
    'description': 'str',
    'display_name': 'str',
    'skill_count': 'int',
    'last_session': 'Union[ProfileSessionPreview, None]',
    'worker_session': 'Union[ProfileWorkerSession, None]',
    'canonical_session': 'Union[ProfileCanonicalSession, None]',
    'ui_meta_revisions': 'dict[str, int]',
    'ui_meta': 'Union[dict[str, Any], None]',
    'has_avatar': 'bool',
}, total=False)

ProfileSessionPreview = TypedDict('ProfileSessionPreview', {
    'id': Required['str'],
    'title': 'str',
    'preview': 'str',
    'started_at': 'Union[float, int]',
    'last_active': 'Union[float, int]',
    'message_count': 'int',
}, total=False)

ProfileWorkerSession = TypedDict('ProfileWorkerSession', {
    'id': Required['str'],
    'source': 'str',
    'title': 'str',
    'last_active': 'Union[float, int]',
}, total=False)

ProfilesConfigureApplied = TypedDict('ProfilesConfigureApplied', {
    'ui_meta': 'Union[bool, None]',
    'ui_meta_revisions': 'Union[dict[str, int], None]',
    'ui_meta_conflicts': 'Union[dict[str, UiMetaConflict], None]',
    'soul': 'Union[bool, None]',
    'description': 'Union[bool, None]',
    'model': 'Union[bool, None]',
    'skills': 'Union[bool, None]',
    'toolsets': 'Union[bool, None]',
    'mcp_servers': 'Union[bool, None]',
}, total=False)

ProfilesConfigureParams = TypedDict('ProfilesConfigureParams', {
    'profile': 'Union[str, None]',
    'name': 'Union[str, None]',
    'ui_meta': 'Union[dict[str, Any], None]',
    'ui_meta_expected_revisions': 'Union[dict[str, int], None]',
    'soul': 'Union[str, None]',
    'description': 'Union[str, None]',
    'model': 'Union[str, None]',
    'provider': 'Union[str, None]',
    'confirm_expensive_model': 'Union[bool, str, None]',
    'disabled_skills': 'Union[builtins.list[str], None]',
    'enabled_toolsets': 'Union[builtins.list[str], None]',
    'enabled_mcp_servers': 'Union[builtins.list[str], None]',
}, total=False)

ProfilesConfigureResult = TypedDict('ProfilesConfigureResult', {
    'ok': Required['bool'],
    'applied': Required['ProfilesConfigureApplied'],
    'confirm_required': 'Union[bool, None]',
    'confirm_message': 'Union[str, None]',
}, total=False)

ProfilesCreateParams = TypedDict('ProfilesCreateParams', {
    'profile': 'Union[str, None]',
    'name': Required['str'],
    'description': 'Union[str, None]',
    'clone_from': 'Union[str, None]',
    'clone_all': 'Union[bool, str, None]',
    'clone_channels': 'Union[bool, str, None]',
    'no_skills': 'Union[bool, str, None]',
    'no_alias': 'Union[bool, str, None]',
    'soul': 'Union[str, None]',
    'model': 'Union[str, None]',
    'provider': 'Union[str, None]',
    'share_auth': 'Union[bool, str, None]',
    'mirror_credentials': 'Union[bool, str, None]',
}, total=False)

ProfilesCreateResult = TypedDict('ProfilesCreateResult', {
    'ok': 'bool',
    'name': Required['str'],
    'path': Required['str'],
    'soul_written': 'bool',
    'model_set': 'bool',
    'mirrored': Required['ProfileMirrored'],
}, total=False)

ProfilesDescribeResult = TypedDict('ProfilesDescribeResult', {
    'name': Required['str'],
    'description': 'str',
    'soul': 'str',
    'model': Required['ProfileModelPin'],
    'skills': 'builtins.list[CapabilityEntry]',
    'toolsets': 'builtins.list[ToolsetEntry]',
    'toolsets_pinned': 'bool',
    'mcp_servers': 'builtins.list[McpServerEntry]',
}, total=False)

ProfilesGetAssetParams = TypedDict('ProfilesGetAssetParams', {
    'profile': 'Union[str, None]',
    'name': 'Union[str, None]',
    'asset': 'Union[str, None]',
}, total=False)

ProfilesGetAssetResult = TypedDict('ProfilesGetAssetResult', {
    'found': Required['bool'],
    'mime': 'Union[str, None]',
    'size': 'Union[int, None]',
    'data': 'Union[str, None]',
}, total=False)

ProfilesListParams = TypedDict('ProfilesListParams', {
    'profile': 'Union[str, None]',
    'include_sessions': 'Union[bool, str, None]',
}, total=False)

ProfilesListResult = TypedDict('ProfilesListResult', {
    'profiles': 'builtins.list[ProfileRow]',
    'bot_mode_protocol': 'bool',
}, total=False)

ProfilesRememberOnboardingParams = TypedDict('ProfilesRememberOnboardingParams', {
    'profile': 'Union[str, None]',
    'answers': 'Union[OnboardingAnswers, None]',
}, total=False)

ProfilesRememberOnboardingResult = TypedDict('ProfilesRememberOnboardingResult', {
    'saved': 'bool',
    'profile': 'str',
    'target': 'str',
}, total=False)

ProfilesSetAssetParams = TypedDict('ProfilesSetAssetParams', {
    'profile': 'Union[str, None]',
    'name': 'Union[str, None]',
    'asset': 'Union[str, None]',
    'data': 'Union[str, None]',
    'clear': 'Union[bool, str, None]',
}, total=False)

ProfilesSetAssetResult = TypedDict('ProfilesSetAssetResult', {
    'ok': 'bool',
    'asset': Required['str'],
    'size': 'int',
    'removed': 'Union[int, None]',
}, total=False)

ProjectFacts = TypedDict('ProjectFacts', {
    'root': Required['str'],
    'manifests': Required['builtins.list[str]'],
    'packageManagers': Required['builtins.list[str]'],
    'verifyCommands': Required['builtins.list[str]'],
    'contextFiles': Required['builtins.list[str]'],
}, total=False)

ProjectFactsParams = TypedDict('ProjectFactsParams', {
    'profile': 'Union[str, None]',
    'cwd': 'Union[str, None]',
}, total=False)

ProjectFactsResult = TypedDict('ProjectFactsResult', {
    'facts': 'Union[ProjectFacts, None]',
}, total=False)

ProjectFolder = TypedDict('ProjectFolder', {
    'path': Required['str'],
    'label': 'Union[str, None]',
    'is_primary': 'bool',
    'added_at': 'Union[int, None]',
}, total=False)

ProjectFolderParams = TypedDict('ProjectFolderParams', {
    'profile': 'Union[str, None]',
    'id': Required['str'],
    'path': Required['str'],
}, total=False)

ProjectIdParams = TypedDict('ProjectIdParams', {
    'profile': 'Union[str, None]',
    'id': Required['str'],
}, total=False)

ProjectInfo = TypedDict('ProjectInfo', {
    'id': Required['str'],
    'slug': Required['str'],
    'name': Required['str'],
    'description': 'Union[str, None]',
    'icon': 'Union[str, None]',
    'color': 'Union[str, None]',
    'board_slug': 'Union[str, None]',
    'primary_path': 'Union[str, None]',
    'archived': 'bool',
    'created_at': Required['int'],
    'folders': 'builtins.list[ProjectFolder]',
}, total=False)

ProjectRef = TypedDict('ProjectRef', {
    'id': Required['str'],
    'slug': Required['str'],
    'name': Required['str'],
    'primary_path': 'Union[str, None]',
}, total=False)

ProjectResult = TypedDict('ProjectResult', {
    'project': Required['ProjectInfo'],
}, total=False)

ProjectTreeLane = TypedDict('ProjectTreeLane', {
    'id': Required['str'],
    'label': Required['str'],
    'path': 'Union[str, None]',
    'isMain': 'bool',
    'isKanban': 'bool',
    'sessions': 'builtins.list[ProjectTreeSession]',
}, total=False)

ProjectTreeNode = TypedDict('ProjectTreeNode', {
    'id': Required['str'],
    'label': Required['str'],
    'path': 'Union[str, None]',
    'color': 'Union[str, None]',
    'icon': 'Union[str, None]',
    'isAuto': 'bool',
    'isNoProject': 'bool',
    'sessionCount': 'int',
    'lastActive': 'float',
    'totalTokens': 'int',
    'totalCostUsd': 'float',
    'repos': 'builtins.list[ProjectTreeRepo]',
    'previewSessions': 'builtins.list[ProjectTreeSession]',
    'sessionIds': 'builtins.list[str]',
}, total=False)

ProjectTreeRepo = TypedDict('ProjectTreeRepo', {
    'id': Required['str'],
    'label': Required['str'],
    'path': 'Union[str, None]',
    'groups': 'builtins.list[ProjectTreeLane]',
    'sessionCount': 'int',
}, total=False)

ProjectTreeSession = TypedDict('ProjectTreeSession', {
    'id': Required['str'],
    'title': 'Union[str, None]',
    'preview': 'Union[str, None]',
    'source': 'Union[str, None]',
    'model': 'Union[str, None]',
    'started_at': 'Union[float, None]',
    'ended_at': 'Union[float, None]',
    'last_active': 'Union[float, None]',
    'message_count': 'int',
    'tool_call_count': 'int',
    'input_tokens': 'int',
    'output_tokens': 'int',
    'is_active': 'bool',
    'cwd': 'Union[str, None]',
    'git_branch': 'Union[str, None]',
    'git_repo_root': 'Union[str, None]',
    'parent_session_id': 'Union[str, None]',
    'pinned': 'Union[bool, None]',
    'unread': 'Union[bool, None]',
    'archived': 'Union[bool, None]',
    'actual_cost_usd': 'Union[float, None]',
    'estimated_cost_usd': 'Union[float, None]',
    'handoff_platform': 'Union[str, None]',
    'handoff_state': 'Union[str, None]',
    '_lineage_root_id': 'Union[str, None]',
    '_lineage_ids': 'Union[builtins.list[str], None]',
    'profile': 'Union[str, None]',
}, total=False)

ProjectsAddFolderParams = TypedDict('ProjectsAddFolderParams', {
    'profile': 'Union[str, None]',
    'id': Required['str'],
    'path': Required['str'],
    'label': 'Union[str, None]',
    'is_primary': 'bool',
}, total=False)

ProjectsArchiveParams = TypedDict('ProjectsArchiveParams', {
    'profile': 'Union[str, None]',
    'id': Required['str'],
    'restore': 'bool',
}, total=False)

ProjectsCreateParams = TypedDict('ProjectsCreateParams', {
    'profile': 'Union[str, None]',
    'name': Required['str'],
    'folders': 'Union[builtins.list[str], None]',
    'slug': 'Union[str, None]',
    'primary_path': 'Union[str, None]',
    'description': 'Union[str, None]',
    'icon': 'Union[str, None]',
    'color': 'Union[str, None]',
    'board_slug': 'Union[str, None]',
    'use': 'bool',
}, total=False)

ProjectsDiscoverReposParams = TypedDict('ProjectsDiscoverReposParams', {
    'profile': 'Union[str, None]',
    'scan': 'bool',
}, total=False)

ProjectsDiscoverReposResult = TypedDict('ProjectsDiscoverReposResult', {
    'repos': Required['builtins.list[DiscoveredRepo]'],
    'discovery_policy': 'Union[RepoDiscoveryPolicy, None]',
}, total=False)

ProjectsForCwdParams = TypedDict('ProjectsForCwdParams', {
    'profile': 'Union[str, None]',
    'cwd': 'Union[str, None]',
}, total=False)

ProjectsForCwdResult = TypedDict('ProjectsForCwdResult', {
    'project': 'Union[ProjectInfo, None]',
    'cwd': Required['str'],
    'branch': 'str',
}, total=False)

ProjectsPayload = TypedDict('ProjectsPayload', {
    'projects': Required['builtins.list[ProjectInfo]'],
    'active_id': 'Union[str, None]',
}, total=False)

ProjectsProjectSessionsParams = TypedDict('ProjectsProjectSessionsParams', {
    'profile': 'Union[str, None]',
    'project_id': Required['str'],
    'session_limit': 'Union[int, None]',
}, total=False)

ProjectsProjectSessionsResult = TypedDict('ProjectsProjectSessionsResult', {
    'project': 'Union[ProjectTreeNode, None]',
}, total=False)

ProjectsRecordReposParams = TypedDict('ProjectsRecordReposParams', {
    'profile': 'Union[str, None]',
    'repos': 'Union[builtins.list[Union[RecordRepoItem, str]], None]',
    'discovery_policy': 'Union[RepoDiscoveryPolicyParams, None]',
}, total=False)

ProjectsRecordReposResult = TypedDict('ProjectsRecordReposResult', {
    'repos': Required['builtins.list[DiscoveredRepo]'],
    'discovery_policy': 'Union[RepoDiscoveryPolicy, None]',
    'accepted': Required['bool'],
}, total=False)

ProjectsSetActiveParams = TypedDict('ProjectsSetActiveParams', {
    'profile': 'Union[str, None]',
    'id': 'Union[str, None]',
}, total=False)

ProjectsTreeParams = TypedDict('ProjectsTreeParams', {
    'profile': 'Union[str, None]',
    'preview_limit': 'Union[int, None]',
    'session_limit': 'Union[int, None]',
}, total=False)

ProjectsTreeResult = TypedDict('ProjectsTreeResult', {
    'projects': Required['builtins.list[ProjectTreeNode]'],
    'active_id': 'Union[str, None]',
    'scoped_session_ids': 'builtins.list[str]',
}, total=False)

ProjectsUpdateParams = TypedDict('ProjectsUpdateParams', {
    'profile': 'Union[str, None]',
    'id': Required['str'],
    'name': 'Union[str, None]',
    'description': 'Union[str, None]',
    'icon': 'Union[str, None]',
    'color': 'Union[str, None]',
    'board_slug': 'Union[str, None]',
}, total=False)

PromptSubmitParams = TypedDict('PromptSubmitParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'text': 'Any',
    'display_kind': 'Union[str, None]',
    'interrupted': 'Union[bool, None]',
    'queued': 'Union[bool, None]',
    'surface': 'Union[str, None]',
    'voice_context': 'Union[str, None]',
    'title_preview': 'Union[str, None]',
    'truncate_before_user_ordinal': 'Union[int, None]',
    'truncate_before_row_id': 'Union[int, None]',
    'truncate_before_message_id': 'Union[str, None]',
    'confirm_truncate': 'Union[bool, None]',
    'confirm_empty_truncate': 'Union[bool, None]',
    'rebind_survivor_row_ids': 'Union[builtins.list[int], None]',
}, total=False)

PromptSubmitResult = TypedDict('PromptSubmitResult', {
    'status': 'Union[PromptSubmitStatus, None]',
    'voice_stopped': 'Union[bool, None]',
    'survivor_user_row_ids': 'Union[builtins.list[Union[int, None]], None]',
    'survivor_row_id_map': 'Union[dict[str, Union[int, None]], None]',
    'turn_isolation': 'Union[bool, None]',
}, total=False)

QueuedPrompt = TypedDict('QueuedPrompt', {
    'user': Required['str'],
}, total=False)

ReactionPayload = TypedDict('ReactionPayload', {
    'kind': Required['str'],
}, total=False)

ReadRangeRequestParams = TypedDict('ReadRangeRequestParams', {
    'session_id': Required['str'],
    'start': 'Union[int, None]',
    'count': 'Union[int, None]',
}, total=False)

RecordRepoItem = TypedDict('RecordRepoItem', {
    'root': Required['str'],
    'label': 'Union[str, None]',
}, total=False)

RelayAgentRow = TypedDict('RelayAgentRow', {
    'profile': 'Union[str, None]',
    'handle': 'Union[str, None]',
    'connection_id': 'Union[str, None]',
    'connection_label': 'Union[str, None]',
    'title': 'Union[str, None]',
    'description': 'Union[str, None]',
    'online': 'Union[bool, None]',
}, total=False)

RelayEnvelope = TypedDict('RelayEnvelope', {
    'id': Required['str'],
    'created_at': Required['Union[int, float]'],
    'from_profile': Required['str'],
    'from_handle': Required['str'],
    'target_connection': Required['str'],
    'target_profile': Required['str'],
    'target_handle': Required['str'],
    'message': Required['str'],
}, total=False)

ReloadEnvParams = TypedDict('ReloadEnvParams', {

}, total=False)

ReloadEnvResult = TypedDict('ReloadEnvResult', {
    'updated': Required['int'],
}, total=False)

ReloadMcpParams = TypedDict('ReloadMcpParams', {
    'session_id': 'Union[str, None]',
    'confirm': 'bool',
    'always': 'bool',
    'rev': 'Union[str, None]',
}, total=False)

ReloadMcpResult = TypedDict('ReloadMcpResult', {
    'status': Required['ReloadMcpStatus'],
    'message': 'Union[str, None]',
    'loaded_rev': 'Union[str, None]',
    'coalesced': 'Union[bool, None]',
    'turn_isolation': 'Union[bool, None]',
    'host_ack': 'Union[Any, None]',
}, total=False)

RepoDiscoveryPolicy = TypedDict('RepoDiscoveryPolicy', {
    'enabled': Required['bool'],
    'roots': Required['builtins.list[str]'],
    'exclude_paths': Required['builtins.list[str]'],
}, total=False)

RepoDiscoveryPolicyParams = TypedDict('RepoDiscoveryPolicyParams', {
    'enabled': 'Union[bool, None]',
    'roots': 'Union[builtins.list[str], None]',
    'exclude_paths': 'Union[builtins.list[str], None]',
    'repo_scan_enabled': 'Union[bool, None]',
    'repo_scan_roots': 'Union[builtins.list[str], None]',
    'repo_scan_exclude_paths': 'Union[builtins.list[str], None]',
}, total=False)

RequestAnswerParams = TypedDict('RequestAnswerParams', {
    'id': Required['str'],
    'result': Required['dict[str, Any]'],
    'profile': 'Union[str, None]',
}, total=False)

RequestAnswerResult = TypedDict('RequestAnswerResult', {
    'status': Required['ClarifyLockStatus'],
}, total=False)

RequestCancelPayload = TypedDict('RequestCancelPayload', {
    'id': Required['str'],
    'method': Required['str'],
    'reason': Required['str'],
}, total=False)

ReviewSummaryPayload = TypedDict('ReviewSummaryPayload', {
    'text': Required['str'],
}, total=False)

RollbackCheckpoint = TypedDict('RollbackCheckpoint', {
    'hash': 'str',
    'timestamp': 'str',
    'message': 'str',
}, total=False)

RollbackDiffParams = TypedDict('RollbackDiffParams', {
    'session_id': Required['str'],
    'hash': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

RollbackDiffResult = TypedDict('RollbackDiffResult', {
    'stat': 'str',
    'diff': 'str',
    'rendered': 'Union[str, None]',
}, total=False)

RollbackListParams = TypedDict('RollbackListParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

RollbackListResult = TypedDict('RollbackListResult', {
    'enabled': Required['bool'],
    'checkpoints': 'builtins.list[RollbackCheckpoint]',
}, total=False)

RollbackRestoreParams = TypedDict('RollbackRestoreParams', {
    'session_id': Required['str'],
    'hash': Required['str'],
    'file_path': 'Union[str, None]',
    'profile': 'Union[str, None]',
}, total=False)

RollbackRestoreResult = TypedDict('RollbackRestoreResult', {
    'success': Required['bool'],
    'restored_to': 'Union[str, None]',
    'reason': 'Union[str, None]',
    'directory': 'Union[str, None]',
    'file': 'Union[str, None]',
    'restored_files': 'Union[builtins.list[str], None]',
    'skipped_user_edits': 'Union[builtins.list[str], None]',
    'skipped_oversize': 'Union[builtins.list[str], None]',
    'failed_deletes': 'Union[builtins.list[str], None]',
    'history_removed': 'Union[int, None]',
    'error': 'Union[str, None]',
    'debug': 'Union[Any, None]',
}, total=False)

Room = TypedDict('Room', {
    'room_id': Required['str'],
    'name': Required['str'],
    'members': Required['builtins.list[RoomMember]'],
    'authority_gateway_id': Required['str'],
    'authority_epoch': Required['int'],
    'revision': Required['int'],
    'created_at': Required['float'],
    'updated_at': Required['float'],
    'idempotent': 'bool',
    'disbanded_at': 'Union[float, None]',
    'latest_seq': 'Union[int, None]',
    'adopted': 'Union[bool, None]',
    'claim_event': 'Union[RoomEvent, None]',
    'authority_claim': 'Union[RoomEvent, None]',
    'event': 'Union[RoomEvent, None]',
}, total=False)

RoomActor = TypedDict('RoomActor', {
    'kind': Required['str'],
    'id': Required['str'],
}, total=False)

RoomAuthority = TypedDict('RoomAuthority', {
    'gateway_id': Required['str'],
    'epoch': Required['int'],
}, total=False)

RoomDriverStatus = TypedDict('RoomDriverStatus', {
    'running': Required['bool'],
    'working': Required['bool'],
    'blocked': Required['bool'],
    'counts': Required['dict[str, int]'],
    'pending_actions': Required['builtins.list[dict[str, Any]]'],
    'peer_routes': Required['builtins.list[PeerRouteStatus]'],
}, total=False)

RoomEvent = TypedDict('RoomEvent', {
    'room_id': Required['str'],
    'seq': Required['int'],
    'event_id': Required['str'],
    'kind': Required['str'],
    'actor': Required['RoomActor'],
    'authority_epoch': 'Union[int, None]',
    'payload': Required['dict[str, Any]'],
    'created_at': Required['float'],
    'idempotent': 'bool',
}, total=False)

RoomExecutionPolicy = TypedDict('RoomExecutionPolicy', {
    'version': Required['int'],
    'target_profile': Required['str'],
    'enabled_toolsets': Required['builtins.list[str]'],
    'approval_mode': Required['str'],
    'max_iterations': Required['int'],
    'policy_digest': Required['str'],
}, total=False)

RoomLinkCatalog = TypedDict('RoomLinkCatalog', {
    'installation_id': Required['str'],
    'protocol_versions': Required['builtins.list[int]'],
    'link_modes': Required['builtins.list[str]'],
    'persistent_process': Required['bool'],
    'text': Required['bool'],
    'attachments': Required['bool'],
    'execution_policy': Required['RoomExecutionPolicy'],
    'catalog_digest': Required['str'],
    'endpoint': 'Union[RoomLinkEndpoint, None]',
}, total=False)

RoomLinkEndpoint = TypedDict('RoomLinkEndpoint', {
    'available': Required['bool'],
    'url': 'Union[str, None]',
    'transport_security': 'Union[str, None]',
    'reason': 'Union[str, None]',
}, total=False)

RoomLinkStatus = TypedDict('RoomLinkStatus', {
    'enabled': Required['bool'],
    'profile': 'Union[str, None]',
    'catalog': 'Union[RoomLinkCatalog, None]',
    'endpoint': 'Union[RoomLinkEndpoint, None]',
    'reason': 'Union[str, None]',
}, total=False)

RoomMember = TypedDict('RoomMember', {
    'member_id': 'Union[str, None]',
    'profile': 'Union[str, None]',
    'handle': 'Union[str, None]',
    'display_name': 'Union[str, None]',
    'target': 'Union[dict[str, Any], None]',
}, total=False)

RoomMemberInput = TypedDict('RoomMemberInput', {
    'member_id': 'Union[str, None]',
    'profile': 'Union[str, None]',
    'handle': 'Union[str, None]',
    'display_name': 'Union[str, None]',
    'target': 'Union[dict[str, Any], None]',
}, total=False)

RoomTaskReceipt = TypedDict('RoomTaskReceipt', {
    'room_id': Required['str'],
    'task_id': Required['str'],
    'thread_id': Required['str'],
    'turn_id': Required['str'],
    'status': Required['str'],
    'execution_generation': Required['int'],
    'cancel_generation': Required['int'],
}, total=False)

RoomTombstone = TypedDict('RoomTombstone', {
    'room_id': Required['str'],
    'disbanded_at': Required['float'],
    'idempotent': Required['bool'],
    'history_expired': 'Union[bool, None]',
    'event': 'Union[RoomEvent, None]',
}, total=False)

SecretRequestParams = TypedDict('SecretRequestParams', {
    'session_id': Required['str'],
    'env_var': Required['str'],
    'prompt': Required['str'],
    'metadata': 'Union[dict[str, Any], None]',
}, total=False)

SeedMessage = TypedDict('SeedMessage', {
    'role': Required['str'],
    'content': 'Union[str, None]',
    'text': 'Union[str, None]',
    'display_kind': 'Union[str, None]',
}, total=False)

SessionActivateParams = TypedDict('SessionActivateParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'cols': 'Union[int, None]',
    'omit_messages': 'bool',
}, total=False)

SessionActivateResult = TypedDict('SessionActivateResult', {
    'session_id': Required['str'],
    'message_count': Required['int'],
    'messages': Required['builtins.list[TranscriptMessage]'],
    'info': Required['SessionLiveInfo'],
    'stored_session_id': 'Union[str, None]',
    'resumed': 'Union[str, None]',
    'session_key': 'Union[str, None]',
    'messages_omitted': 'Union[bool, None]',
    'hydrating': 'Union[bool, None]',
    'running': 'Union[bool, None]',
    'turn_started_at': 'Union[float, None]',
    'started_at': 'Union[float, None]',
    'status': 'Union[str, None]',
    'inflight': 'Union[InflightTurn, None]',
    'queued': 'Union[QueuedPrompt, None]',
    'pending_approval': 'Union[PendingApproval, None]',
    'open_requests': 'Union[builtins.list[OpenRequestEntry], None]',
    'pending_connection': 'Union[ConnectionRequestPayload, None]',
    'todo_state': 'Union[TodoState, None]',
    'auto_continue': 'Union[AutoContinue, None]',
}, total=False)

SessionActiveItem = TypedDict('SessionActiveItem', {
    'current': Required['bool'],
    'id': Required['str'],
    'last_active': Required['float'],
    'message_count': Required['int'],
    'model': Required['str'],
    'preview': Required['str'],
    'session_key': Required['str'],
    'started_at': Required['float'],
    'status': Required['LiveSessionStatus'],
    'title': Required['str'],
}, total=False)

SessionActiveListParams = TypedDict('SessionActiveListParams', {
    'profile': 'Union[str, None]',
    'current_session_id': 'Union[str, None]',
}, total=False)

SessionActiveListResult = TypedDict('SessionActiveListResult', {
    'sessions': Required['builtins.list[SessionActiveItem]'],
}, total=False)

SessionBranchParams = TypedDict('SessionBranchParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'name': 'Union[str, None]',
    'count': 'Union[int, None]',
}, total=False)

SessionBranchResult = TypedDict('SessionBranchResult', {
    'session_id': Required['str'],
    'stored_session_id': Required['str'],
    'title': Required['str'],
    'parent': Required['str'],
    'message_count': Required['int'],
    'messages': Required['builtins.list[TranscriptMessage]'],
    'info': Required['SessionLiveInfo'],
}, total=False)

SessionCloseParams = TypedDict('SessionCloseParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

SessionCloseResult = TypedDict('SessionCloseResult', {
    'closed': Required['bool'],
}, total=False)

SessionCompressParams = TypedDict('SessionCompressParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'focus_topic': 'Union[str, None]',
}, total=False)

SessionCompressResult = TypedDict('SessionCompressResult', {
    'status': 'Union[str, None]',
    'removed': 'Union[int, None]',
    'before_messages': 'Union[int, None]',
    'after_messages': 'Union[int, None]',
    'before_tokens': 'Union[int, None]',
    'after_tokens': 'Union[int, None]',
    'summary': 'Union[CompressionSummary, None]',
    'usage': 'Union[Usage, None]',
    'info': 'Union[SessionLiveInfo, None]',
    'messages': 'Union[builtins.list[TranscriptMessage], None]',
    'compressed': 'Union[bool, None]',
    'lock_held': 'Union[bool, None]',
    'message': 'Union[str, None]',
    'turn_isolation': 'Union[bool, None]',
    'host_ack': 'Union[dict[str, Any], None]',
}, total=False)

SessionContextBreakdownParams = TypedDict('SessionContextBreakdownParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

SessionContextBreakdownResult = TypedDict('SessionContextBreakdownResult', {
    'categories': Required['builtins.list[ContextCategory]'],
    'context_max': Required['int'],
    'context_percent': Required['int'],
    'context_used': Required['int'],
    'estimated_total': Required['int'],
    'context_estimated': Required['bool'],
    'context_source': Required['str'],
    'model': Required['str'],
    'context_files': 'builtins.list[ContextFileSource]',
}, total=False)

SessionControlArgs = TypedDict('SessionControlArgs', {
    'text': 'Union[str, None]',
    'index': 'Union[int, None]',
}, total=False)

SessionControlDispatch = TypedDict('SessionControlDispatch', {
    'type': Required['Union[str, None]'],
    'output': Required['Union[str, None]'],
    'notice': Required['Union[str, None]'],
    'message': Required['Union[str, None]'],
    'display': Required['Union[str, None]'],
}, total=False)

SessionControlParams = TypedDict('SessionControlParams', {
    'profile': 'Union[str, None]',
    'session_id': Required['str'],
    'action': Required['str'],
    'args': 'Union[SessionControlArgs, None]',
}, total=False)

SessionControlReadParams = TypedDict('SessionControlReadParams', {
    'profile': 'Union[str, None]',
    'session_id': Required['str'],
}, total=False)

SessionControlReadResult = TypedDict('SessionControlReadResult', {
    'control': Required['SessionControlSnapshot'],
}, total=False)

SessionControlResult = TypedDict('SessionControlResult', {
    'control': Required['SessionControlSnapshot'],
    'dispatch': Required['SessionControlDispatch'],
}, total=False)

SessionControlSnapshot = TypedDict('SessionControlSnapshot', {
    'goal': Required['Union[GoalSnapshot, None]'],
    'loop': Required['Union[LoopSnapshot, None]'],
    'heartbeat': Required['Union[HeartbeatSnapshot, None]'],
    'revision': Required['str'],
    'updated_at': Required['float'],
}, total=False)

SessionControlUpdatePayload = TypedDict('SessionControlUpdatePayload', {
    'control': Required['SessionControlSnapshot'],
}, total=False)

SessionCorrectionParams = TypedDict('SessionCorrectionParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'text': Required['str'],
}, total=False)

SessionCorrectionResult = TypedDict('SessionCorrectionResult', {
    'status': Required['CorrectionStatus'],
    'text': Required['str'],
}, total=False)

SessionCreateParams = TypedDict('SessionCreateParams', {
    'profile': 'Union[str, None]',
    'cols': 'Union[int, None]',
    'source': 'Union[str, None]',
    'cwd': 'Union[str, None]',
    'messages': 'Union[builtins.list[SeedMessage], None]',
    'parent_session_id': 'Union[str, None]',
    'title': 'Union[str, None]',
    'model': 'Union[str, None]',
    'provider': 'Union[str, None]',
    'reasoning_effort': 'Union[str, None]',
    'fast': 'Union[bool, None]',
    'close_on_disconnect': 'bool',
    'hidden': 'bool',
    'room_plumbing': 'bool',
    'follow_profile_config': 'bool',
}, total=False)

SessionCreateResult = TypedDict('SessionCreateResult', {
    'session_id': Required['str'],
    'stored_session_id': Required['str'],
    'message_count': Required['int'],
    'messages': Required['builtins.list[TranscriptMessage]'],
    'info': Required['SessionLiveInfo'],
}, total=False)

SessionCwdSetParams = TypedDict('SessionCwdSetParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'cwd': Required['str'],
}, total=False)

SessionCwdSetResult = TypedDict('SessionCwdSetResult', {
    'model': 'str',
    'provider': 'str',
    'reasoning_effort': 'str',
    'reasoning_effort_wire': 'str',
    'service_tier': 'str',
    'fast': 'bool',
    'yolo': 'bool',
    'approval_mode': 'str',
    'tools': 'dict[str, builtins.list[str]]',
    'skills': 'dict[str, builtins.list[str]]',
    'cwd': 'str',
    'branch': 'Union[str, None]',
    'project': 'Union[ProjectRef, None]',
    'terminal_backend': 'str',
    'personality': 'str',
    'running': 'bool',
    'turn_started_at': 'Union[float, None]',
    'title': 'str',
    'stored_session_id': 'str',
    'desktop_contract': 'Union[int, str, None]',
    'version': 'str',
    'release_date': 'str',
    'update_behind': 'Union[Any, None]',
    'update_command': 'str',
    'usage': 'Union[Usage, None]',
    'profile_name': 'Union[str, None]',
    'mcp_servers': 'builtins.list[McpServerStatus]',
    'system_prompt': 'Union[str, None]',
    'credential_warning': 'Union[str, None]',
    'lazy': 'Union[bool, None]',
}, total=False)

SessionDeleteParams = TypedDict('SessionDeleteParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

SessionDeleteResult = TypedDict('SessionDeleteResult', {
    'deleted': Required['str'],
}, total=False)

SessionEventsSinceParams = TypedDict('SessionEventsSinceParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'last_seen': 'Union[int, None]',
}, total=False)

SessionEventsSinceResult = TypedDict('SessionEventsSinceResult', {
    'events': Required['builtins.list[dict[str, Any]]'],
    'latest_seq': Required['int'],
    'truncated': Required['bool'],
    'count': Required['int'],
    'epoch': Required['str'],
    'open_requests': Required['builtins.list[OpenRequestEntry]'],
}, total=False)

SessionEventsStatsParams = TypedDict('SessionEventsStatsParams', {
    'profile': 'Union[str, None]',
}, total=False)

SessionEventsStatsResult = TypedDict('SessionEventsStatsResult', {
    'sessions': Required['int'],
    'events': Required['int'],
    'bytes': Required['int'],
    'max_per_session': Required['int'],
    'max_bytes_per_session': Required['int'],
    'max_bytes_process': Required['int'],
}, total=False)

SessionForeignIdParams = TypedDict('SessionForeignIdParams', {
    'profile': 'Union[str, None]',
    'id': 'Union[str, None]',
}, total=False)

SessionForeignImportResult = TypedDict('SessionForeignImportResult', {
    'session_id': Required['str'],
    'already_imported': 'bool',
}, total=False)

SessionForeignListParams = TypedDict('SessionForeignListParams', {
    'profile': 'Union[str, None]',
    'source': 'Union[ForeignSource, None]',
    'offset': 'Union[int, None]',
    'limit': 'Union[int, None]',
}, total=False)

SessionForeignListResult = TypedDict('SessionForeignListResult', {
    'sessions': 'builtins.list[ForeignSessionRow]',
    'next_offset': 'Union[int, None]',
    'host': Required['str'],
    'unreadable': 'int',
}, total=False)

SessionForeignPreviewResult = TypedDict('SessionForeignPreviewResult', {
    'messages': 'builtins.list[ForeignTurn]',
    'total': 'int',
    'truncated': 'bool',
    'already_imported': 'Union[str, None]',
    'cwd': 'Union[str, None]',
}, total=False)

SessionHistoryParams = TypedDict('SessionHistoryParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

SessionHistoryResult = TypedDict('SessionHistoryResult', {
    'count': Required['int'],
    'messages': Required['builtins.list[TranscriptMessage]'],
}, total=False)

SessionInterruptParams = TypedDict('SessionInterruptParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'expected_hosted_task_id': 'Union[str, None]',
}, total=False)

SessionInterruptResult = TypedDict('SessionInterruptResult', {
    'status': Required['InterruptStatus'],
    'interrupted': 'Union[bool, None]',
    'turn_isolation': 'Union[bool, None]',
}, total=False)

SessionListParams = TypedDict('SessionListParams', {
    'profile': 'Union[str, None]',
    'title': 'Union[str, None]',
    'limit': 'Union[int, None]',
    'include_hidden': 'bool',
}, total=False)

SessionListResult = TypedDict('SessionListResult', {
    'sessions': Required['builtins.list[SessionListRow]'],
}, total=False)

SessionListRow = TypedDict('SessionListRow', {
    'id': Required['str'],
    'resolved_id': 'Union[str, None]',
    'title': 'str',
    'preview': 'str',
    'started_at': 'float',
    'message_count': 'int',
    'source': 'str',
}, total=False)

SessionLiveInfo = TypedDict('SessionLiveInfo', {
    'model': 'str',
    'provider': 'str',
    'reasoning_effort': 'str',
    'reasoning_effort_wire': 'str',
    'service_tier': 'str',
    'fast': 'bool',
    'yolo': 'bool',
    'approval_mode': 'str',
    'tools': 'dict[str, builtins.list[str]]',
    'skills': 'dict[str, builtins.list[str]]',
    'cwd': 'str',
    'branch': 'Union[str, None]',
    'project': 'Union[ProjectRef, None]',
    'terminal_backend': 'str',
    'personality': 'str',
    'running': 'bool',
    'turn_started_at': 'Union[float, None]',
    'title': 'str',
    'stored_session_id': 'str',
    'desktop_contract': 'Union[int, str, None]',
    'version': 'str',
    'release_date': 'str',
    'update_behind': 'Union[Any, None]',
    'update_command': 'str',
    'usage': 'Union[Usage, None]',
    'profile_name': 'Union[str, None]',
    'mcp_servers': 'builtins.list[McpServerStatus]',
    'system_prompt': 'Union[str, None]',
    'credential_warning': 'Union[str, None]',
    'lazy': 'Union[bool, None]',
}, total=False)

SessionMostRecentParams = TypedDict('SessionMostRecentParams', {
    'profile': 'Union[str, None]',
}, total=False)

SessionMostRecentResult = TypedDict('SessionMostRecentResult', {
    'session_id': Required['Union[str, None]'],
    'title': 'Union[str, None]',
    'started_at': 'Union[float, None]',
    'source': 'Union[str, None]',
}, total=False)

SessionParams = TypedDict('SessionParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

SessionReclaimedPayload = TypedDict('SessionReclaimedPayload', {
    'session_id': Required['str'],
    'stored_session_id': Required['str'],
    'reason': Required['str'],
}, total=False)

SessionResumeParams = TypedDict('SessionResumeParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'cols': 'Union[int, None]',
    'source': 'Union[str, None]',
    'lazy': 'bool',
    'defer_history': 'bool',
    'omit_messages': 'bool',
    'eager_build': 'bool',
    'close_on_disconnect': 'bool',
}, total=False)

SessionResumeProgressPayload = TypedDict('SessionResumeProgressPayload', {
    'phase': Required['str'],
    'status': Required['ResumePhaseStatus'],
    'message_count': 'Union[int, None]',
    'message': 'Union[str, None]',
}, total=False)

SessionResumeResult = TypedDict('SessionResumeResult', {
    'session_id': Required['str'],
    'message_count': Required['int'],
    'messages': Required['builtins.list[TranscriptMessage]'],
    'info': Required['SessionLiveInfo'],
    'stored_session_id': 'Union[str, None]',
    'resumed': 'Union[str, None]',
    'session_key': 'Union[str, None]',
    'messages_omitted': 'Union[bool, None]',
    'hydrating': 'Union[bool, None]',
    'running': 'Union[bool, None]',
    'turn_started_at': 'Union[float, None]',
    'started_at': 'Union[float, None]',
    'status': 'Union[str, None]',
    'inflight': 'Union[InflightTurn, None]',
    'queued': 'Union[QueuedPrompt, None]',
    'pending_approval': 'Union[PendingApproval, None]',
    'open_requests': 'Union[builtins.list[OpenRequestEntry], None]',
    'pending_connection': 'Union[ConnectionRequestPayload, None]',
    'todo_state': 'Union[TodoState, None]',
    'auto_continue': 'Union[AutoContinue, None]',
}, total=False)

SessionSaveParams = TypedDict('SessionSaveParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

SessionSaveResult = TypedDict('SessionSaveResult', {
    'file': 'Union[str, None]',
}, total=False)

SessionSetHiddenParams = TypedDict('SessionSetHiddenParams', {
    'session_id': Required['str'],
    'hidden': 'bool',
    'profile': 'Union[str, None]',
}, total=False)

SessionSetHiddenResult = TypedDict('SessionSetHiddenResult', {
    'hidden': Required['bool'],
    'session_key': Required['str'],
}, total=False)

SessionStatusParams = TypedDict('SessionStatusParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

SessionStatusResult = TypedDict('SessionStatusResult', {
    'output': Required['str'],
}, total=False)

SessionTitleParams = TypedDict('SessionTitleParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'title': 'Union[str, None]',
}, total=False)

SessionTitlePayload = TypedDict('SessionTitlePayload', {
    'session_id': Required['str'],
    'title': Required['str'],
}, total=False)

SessionTitleResult = TypedDict('SessionTitleResult', {
    'title': Required['str'],
    'session_key': 'Union[str, None]',
    'pending': 'Union[bool, None]',
}, total=False)

SessionUndoParams = TypedDict('SessionUndoParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

SessionUndoResult = TypedDict('SessionUndoResult', {
    'removed': Required['int'],
}, total=False)

SessionUsageParams = TypedDict('SessionUsageParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

SessionUsagePayload = TypedDict('SessionUsagePayload', {
    'usage': Required['Usage'],
}, total=False)

SessionUsageResult = TypedDict('SessionUsageResult', {
    'model': 'str',
    'input': 'int',
    'output': 'int',
    'reasoning': 'int',
    'prompt': 'int',
    'completion': 'int',
    'total': 'int',
    'calls': 'int',
    'compressions': 'Union[int, None]',
    'context_used': 'Union[int, None]',
    'context_max': 'Union[int, None]',
    'context_percent': 'Union[int, None]',
    'context_source': 'Union[str, None]',
    'context_estimated': 'Union[bool, None]',
    'cache_hit_pct': 'Union[int, None]',
    'cache_read': 'Union[int, None]',
    'cache_write': 'Union[int, None]',
    'avg_latency_s': 'Union[float, None]',
    'avg_tps': 'Union[float, None]',
    'active_subagents': 'Union[int, None]',
    'dev_credits_spent_micros': 'Union[int, None]',
    'cost_usd': 'Union[float, None]',
    'cost_status': 'Union[str, None]',
    'credits_lines': 'Union[builtins.list[str], None]',
}, total=False)

SessionWorkspaceMoveParams = TypedDict('SessionWorkspaceMoveParams', {
    'profile': 'Union[str, None]',
    'session_key': Required['str'],
    'cwd': Required['str'],
}, total=False)

SessionWorkspaceMoveResult = TypedDict('SessionWorkspaceMoveResult', {
    'cwd': Required['str'],
    'branch': 'Union[str, None]',
    'git_repo_root': 'Union[str, None]',
}, total=False)

SetupReadyPayload = TypedDict('SetupReadyPayload', {
    'provider_configured': Required['bool'],
    'inference_provider': Required['str'],
    'free_tier': Required['bool'],
    'has_identity': Required['bool'],
    'other_providers': Required['bool'],
    'error': 'str',
    'error_code': 'Union[str, None]',
    'retryable': 'Union[bool, None]',
    'retry_after': 'Union[int, None]',
    'finished_at': Required['float'],
}, total=False)

SetupRuntimeCheckParams = TypedDict('SetupRuntimeCheckParams', {
    'profile': 'Union[str, None]',
    'provider': 'Union[str, None]',
}, total=False)

SetupRuntimeCheckResult = TypedDict('SetupRuntimeCheckResult', {
    'ok': Required['bool'],
    'provider': 'Union[str, None]',
    'model': 'Union[str, None]',
    'source': 'Union[str, None]',
    'error': 'Union[str, None]',
    'free_tier': 'Union[bool, None]',
    'profile': 'Union[str, None]',
}, total=False)

SetupStatusResult = TypedDict('SetupStatusResult', {
    'provider_configured': 'Union[bool, None]',
    'ready': 'Union[bool, None]',
    'free_tier': 'Union[bool, None]',
    'other_providers': 'Union[bool, None]',
    'inference_provider': 'Union[str, None]',
    'profile': 'Union[str, None]',
    'ok': 'Union[bool, None]',
    'error': 'Union[str, None]',
}, total=False)

ShellExecParams = TypedDict('ShellExecParams', {
    'command': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

ShellExecResult = TypedDict('ShellExecResult', {
    'stdout': Required['str'],
    'stderr': Required['str'],
    'code': Required['int'],
}, total=False)

SideAgentCompletePayload = TypedDict('SideAgentCompletePayload', {
    'task_id': Required['str'],
    'text': Required['str'],
    'question': 'Union[str, None]',
}, total=False)

SideAgentParams = TypedDict('SideAgentParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'text': Required['str'],
}, total=False)

SkillBrowseItem = TypedDict('SkillBrowseItem', {
    'name': 'str',
    'description': 'str',
    'source': 'str',
    'trust': 'Union[str, None]',
    'identifier': 'Union[str, None]',
}, total=False)

SkillCatalogEntry = TypedDict('SkillCatalogEntry', {
    'usage': 'int',
    'origin': 'str',
}, total=False)

SkillCommandRef = TypedDict('SkillCommandRef', {
    'name': Required['str'],
    'description': 'str',
}, total=False)

SkillHubHit = TypedDict('SkillHubHit', {
    'name': Required['str'],
    'description': Required['str'],
}, total=False)

SkillInspectInfo = TypedDict('SkillInspectInfo', {
    'name': 'Union[str, None]',
    'description': 'Union[str, None]',
    'source': 'Union[str, None]',
    'identifier': 'Union[str, None]',
    'tags': 'Union[builtins.list[str], None]',
    'skill_md_preview': 'Union[str, None]',
}, total=False)

SkillsManageParams = TypedDict('SkillsManageParams', {
    'profile': 'Union[str, None]',
    'action': 'SkillsAction',
    'query': 'Union[str, None]',
    'page': 'Union[int, None]',
    'page_size': 'Union[int, None]',
}, total=False)

SkillsManageResult = TypedDict('SkillsManageResult', {
    'skills': 'Union[dict[str, builtins.list[str]], None]',
    'results': 'Union[builtins.list[SkillHubHit], None]',
    'installed': 'Union[bool, None]',
    'name': 'Union[str, None]',
    'items': 'Union[builtins.list[SkillBrowseItem], None]',
    'page': 'Union[int, None]',
    'total_pages': 'Union[int, None]',
    'total': 'Union[int, None]',
    'info': 'Union[SkillInspectInfo, None]',
}, total=False)

SkillsReloadDiff = TypedDict('SkillsReloadDiff', {
    'added': 'builtins.list[SkillCommandRef]',
    'removed': 'builtins.list[SkillCommandRef]',
    'unchanged': 'builtins.list[str]',
    'total': 'int',
    'commands': 'int',
}, total=False)

SkillsReloadParams = TypedDict('SkillsReloadParams', {
    'session_id': 'Union[str, None]',
}, total=False)

SkillsReloadResult = TypedDict('SkillsReloadResult', {
    'output': Required['str'],
    'result': Required['SkillsReloadDiff'],
}, total=False)

SkinPayload = TypedDict('SkinPayload', {
    'name': 'str',
    'description': 'str',
    'colors': 'dict[str, str]',
    'light_colors': 'dict[str, str]',
    'dark_colors': 'dict[str, str]',
    'branding': 'dict[str, str]',
    'banner_logo': 'str',
    'banner_hero': 'str',
    'tool_prefix': 'str',
    'help_header': 'str',
}, total=False)

SlashExecParams = TypedDict('SlashExecParams', {
    'session_id': Required['str'],
    'command': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

SlashExecResult = TypedDict('SlashExecResult', {
    'output': 'Union[str, None]',
    'warning': 'Union[str, None]',
    'type': 'Union[DispatchType, None]',
    'target': 'Union[str, None]',
    'message': 'Union[str, None]',
    'notice': 'Union[str, None]',
    'display': 'Union[str, None]',
    'name': 'Union[str, None]',
    'status': 'Union[str, None]',
}, total=False)

SpawnTreeEntry = TypedDict('SpawnTreeEntry', {
    'path': Required['str'],
    'session_id': 'Union[str, None]',
    'started_at': 'Union[float, None]',
    'finished_at': 'Union[float, None]',
    'label': 'str',
    'count': 'int',
}, total=False)

SpawnTreeListParams = TypedDict('SpawnTreeListParams', {
    'profile': 'Union[str, None]',
    'session_id': 'Union[str, None]',
    'cross_session': 'bool',
    'limit': 'Union[int, None]',
}, total=False)

SpawnTreeListResult = TypedDict('SpawnTreeListResult', {
    'entries': Required['builtins.list[SpawnTreeEntry]'],
}, total=False)

SpawnTreeLoadParams = TypedDict('SpawnTreeLoadParams', {
    'profile': 'Union[str, None]',
    'path': Required['str'],
}, total=False)

SpawnTreeLoadResult = TypedDict('SpawnTreeLoadResult', {
    'session_id': 'Union[str, None]',
    'started_at': 'Union[float, None]',
    'finished_at': 'Union[float, None]',
    'label': 'Union[str, None]',
    'subagents': 'builtins.list[dict[str, Any]]',
}, total=False)

SpawnTreeSaveParams = TypedDict('SpawnTreeSaveParams', {
    'profile': 'Union[str, None]',
    'subagents': Required['builtins.list[dict[str, Any]]'],
    'session_id': 'Union[str, None]',
    'started_at': 'Union[float, None]',
    'finished_at': 'Union[float, None]',
    'label': 'Union[str, None]',
}, total=False)

SpawnTreeSaveResult = TypedDict('SpawnTreeSaveResult', {
    'path': Required['str'],
    'session_id': Required['str'],
}, total=False)

StatusUpdatePayload = TypedDict('StatusUpdatePayload', {
    'kind': Required['str'],
    'text': Required['str'],
}, total=False)

StreamDeltaPayload = TypedDict('StreamDeltaPayload', {
    'text': Required['str'],
    'rendered': 'Union[str, None]',
    'verbose': 'Union[bool, None]',
}, total=False)

SubagentEventPayload = TypedDict('SubagentEventPayload', {
    'goal': Required['str'],
    'task_count': Required['int'],
    'task_index': Required['int'],
    'subagent_id': 'Union[str, None]',
    'parent_id': 'Union[str, None]',
    'child_session_id': 'Union[str, None]',
    'delegation_id': 'Union[str, None]',
    'depth': 'Union[int, None]',
    'model': 'Union[str, None]',
    'tool_count': 'Union[int, None]',
    'toolsets': 'Union[builtins.list[str], None]',
    'input_tokens': 'Union[int, None]',
    'output_tokens': 'Union[int, None]',
    'reasoning_tokens': 'Union[int, None]',
    'api_calls': 'Union[int, None]',
    'files_read': 'Union[builtins.list[str], None]',
    'files_written': 'Union[builtins.list[str], None]',
    'output_tail': 'Union[builtins.list[SubagentOutputTailEntry], None]',
    'tool_name': 'Union[str, None]',
    'text': 'Union[str, None]',
    'status': 'Union[SubagentStatus, None]',
    'summary': 'Union[str, None]',
    'duration_seconds': 'Union[float, None]',
    'tool_preview': 'Union[str, None]',
}, total=False)

SubagentIdParams = TypedDict('SubagentIdParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'subagent_id': Required['str'],
}, total=False)

SubagentInterruptResult = TypedDict('SubagentInterruptResult', {
    'found': Required['bool'],
    'subagent_id': Required['str'],
}, total=False)

SubagentListResult = TypedDict('SubagentListResult', {
    'subagents': 'builtins.list[SubagentSnapshot]',
    'delegations': 'builtins.list[dict[str, Any]]',
}, total=False)

SubagentOutputTailEntry = TypedDict('SubagentOutputTailEntry', {
    'tool': Required['str'],
    'preview': Required['str'],
    'is_error': Required['bool'],
}, total=False)

SubagentSnapshot = TypedDict('SubagentSnapshot', {
    'subagent_id': Required['str'],
    'parent_id': 'Union[str, None]',
    'depth': 'Union[int, None]',
    'goal': 'Union[str, None]',
    'delegation_id': 'Union[str, None]',
    'model': 'Union[str, None]',
    'started_at': 'Union[float, None]',
    'status': 'Union[SubagentStatus, None]',
    'tool_count': 'Union[int, None]',
    'last_tool': 'Union[str, None]',
    'accepting_steer': 'Union[bool, None]',
}, total=False)

SubagentSteerParams = TypedDict('SubagentSteerParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'subagent_id': Required['str'],
    'text': Required['str'],
}, total=False)

SubagentSteerResult = TypedDict('SubagentSteerResult', {
    'status': Required['SteerStatus'],
    'subagent_id': Required['str'],
    'text': Required['str'],
}, total=False)

SubagentTailResult = TypedDict('SubagentTailResult', {
    'subagent_id': Required['str'],
    'available': 'bool',
    'text': 'str',
    'truncated': 'bool',
}, total=False)

SubscriptionChangeParams = TypedDict('SubscriptionChangeParams', {
    'profile': 'Union[str, None]',
    'subscription_type_id': 'Union[str, None]',
    'cancel': 'bool',
}, total=False)

SubscriptionPreviewParams = TypedDict('SubscriptionPreviewParams', {
    'profile': 'Union[str, None]',
    'subscription_type_id': 'Union[str, None]',
}, total=False)

SubscriptionPreviewResult = TypedDict('SubscriptionPreviewResult', {
    'ok': Required['bool'],
    'error': 'Union[str, None]',
    'message': 'Union[str, None]',
    'portal_url': 'Union[str, None]',
    'retry_after': 'Union[int, float, None]',
    'payload': 'Union[dict[str, Any], None]',
    'actor': 'Union[str, None]',
    'code': 'Union[str, None]',
    'recovery': 'Union[str, None]',
    'effect': 'Union[SubscriptionChangeEffect, None]',
    'reason': 'Union[str, None]',
    'current_tier_id': 'Union[str, None]',
    'current_tier_name': 'Union[str, None]',
    'target_tier_id': 'Union[str, None]',
    'target_tier_name': 'Union[str, None]',
    'monthly_credits_delta': 'Union[str, None]',
    'amount_due_now_cents': 'Union[int, None]',
    'effective_at': 'Union[str, None]',
}, total=False)

SubscriptionStateResult = TypedDict('SubscriptionStateResult', {
    'ok': Required['bool'],
    'logged_in': Required['bool'],
    'is_admin': 'Union[bool, None]',
    'can_change_plan': 'Union[bool, None]',
    'org_name': 'Union[str, None]',
    'org_id': 'Union[str, None]',
    'role': 'Union[str, None]',
    'context': 'Union[SubscriptionContext, None]',
    'current': 'Union[CurrentSubscription, None]',
    'tiers': 'Union[builtins.list[SubscriptionTierOption], None]',
    'portal_url': 'Union[str, None]',
    'error': 'Union[str, None]',
    'usage': 'Union[UsageModel, None]',
}, total=False)

SubscriptionTierOption = TypedDict('SubscriptionTierOption', {
    'tier_id': Required['str'],
    'name': Required['str'],
    'tier_order': Required['int'],
    'dollars_per_month_display': Required['str'],
    'monthly_credits': 'Union[str, None]',
    'is_current': Required['bool'],
    'is_enabled': Required['bool'],
}, total=False)

SubscriptionUpgradeParams = TypedDict('SubscriptionUpgradeParams', {
    'profile': 'Union[str, None]',
    'subscription_type_id': 'Union[str, None]',
    'idempotency_key': 'Union[str, None]',
}, total=False)

SubscriptionUpgradeResult = TypedDict('SubscriptionUpgradeResult', {
    'ok': Required['bool'],
    'error': 'Union[str, None]',
    'message': 'Union[str, None]',
    'portal_url': 'Union[str, None]',
    'retry_after': 'Union[int, float, None]',
    'payload': 'Union[dict[str, Any], None]',
    'actor': 'Union[str, None]',
    'code': 'Union[str, None]',
    'recovery': 'Union[str, None]',
    'status': 'Union[str, None]',
    'target_tier_name': 'Union[str, None]',
    'recovery_url': 'Union[str, None]',
    'reason': 'Union[str, None]',
    'idempotency_key': 'Union[str, None]',
}, total=False)

SudoRequestParams = TypedDict('SudoRequestParams', {
    'session_id': Required['str'],
    'command': 'str',
}, total=False)

SystemBatteryParams = TypedDict('SystemBatteryParams', {
    'profile': 'Union[str, None]',
}, total=False)

SystemBatteryResult = TypedDict('SystemBatteryResult', {
    'available': Required['bool'],
    'percent': 'Union[int, None]',
    'plugged': 'Union[bool, None]',
    'category': 'BatteryCategory',
}, total=False)

TaskIdResult = TypedDict('TaskIdResult', {
    'task_id': Required['str'],
}, total=False)

TerminalClosePayload = TypedDict('TerminalClosePayload', {
    'process_id': Required['str'],
}, total=False)

TerminalOutputPayload = TypedDict('TerminalOutputPayload', {
    'process_id': Required['str'],
    'chunk': Required['str'],
}, total=False)

TerminalResizeParams = TypedDict('TerminalResizeParams', {
    'session_id': Required['str'],
    'profile': 'Union[str, None]',
    'cols': 'Union[int, None]',
}, total=False)

TerminalResizeResult = TypedDict('TerminalResizeResult', {
    'cols': Required['int'],
}, total=False)

TipShowPayload = TypedDict('TipShowPayload', {
    'selector': Required['str'],
    'text': Required['str'],
    'title': 'Union[str, None]',
    'side': 'Union[str, None]',
}, total=False)

TodoState = TypedDict('TodoState', {
    'todos': Required['builtins.list[dict[str, Any]]'],
    'revision': Required['int'],
}, total=False)

TodoUpdatedPayload = TypedDict('TodoUpdatedPayload', {
    'todos': Required['builtins.list[Any]'],
    'revision': Required['int'],
}, total=False)

ToolCompletePayload = TypedDict('ToolCompletePayload', {
    'tool_id': Required['str'],
    'name': Required['str'],
    'args': 'Union[dict[str, Any], None]',
    'duration_s': 'Union[float, None]',
    'result': 'Any',
    'summary': 'Union[str, None]',
    'result_text': 'Union[str, None]',
    'inline_diff': 'Union[str, None]',
    'todos': 'Union[builtins.list[Any], None]',
    'revision': 'Union[int, None]',
}, total=False)

ToolGeneratingPayload = TypedDict('ToolGeneratingPayload', {
    'name': Required['str'],
}, total=False)

ToolOutputRiskPayload = TypedDict('ToolOutputRiskPayload', {
    'tool_id': Required['str'],
    'name': Required['str'],
    'risk': Required['str'],
    'findings': Required['builtins.list[str]'],
    'redacted': Required['bool'],
}, total=False)

ToolShowRow = TypedDict('ToolShowRow', {
    'name': Required['str'],
    'description': Required['str'],
}, total=False)

ToolShowSection = TypedDict('ToolShowSection', {
    'name': Required['str'],
    'tools': Required['builtins.list[ToolShowRow]'],
}, total=False)

ToolStartPayload = TypedDict('ToolStartPayload', {
    'tool_id': Required['str'],
    'name': Required['str'],
    'context': 'Union[str, None]',
    'args': 'Union[dict[str, Any], None]',
    'args_text': 'Union[str, None]',
    'preview': 'Union[str, None]',
}, total=False)

ToolsConfigureParams = TypedDict('ToolsConfigureParams', {
    'action': Required['ToolsAction'],
    'names': Required['builtins.list[str]'],
    'session_id': 'Union[str, None]',
    'profile': 'Union[str, None]',
}, total=False)

ToolsConfigureResult = TypedDict('ToolsConfigureResult', {
    'changed': Required['builtins.list[str]'],
    'enabled_toolsets': Required['builtins.list[str]'],
    'info': 'Union[SessionLiveInfo, None]',
    'missing_servers': Required['builtins.list[str]'],
    'reset': Required['bool'],
    'unknown': Required['builtins.list[str]'],
}, total=False)

ToolsShowResult = TypedDict('ToolsShowResult', {
    'sections': Required['builtins.list[ToolShowSection]'],
    'total': Required['int'],
}, total=False)

ToolsetEntry = TypedDict('ToolsetEntry', {
    'name': Required['str'],
    'enabled': 'bool',
    'label': 'str',
    'description': 'str',
    'tool_count': 'int',
}, total=False)

ToolsetRow = TypedDict('ToolsetRow', {
    'name': Required['str'],
    'description': Required['str'],
    'tool_count': Required['int'],
    'enabled': Required['bool'],
    'tools': 'Union[builtins.list[str], None]',
}, total=False)

ToolsetsListResult = TypedDict('ToolsetsListResult', {
    'toolsets': Required['builtins.list[ToolsetRow]'],
}, total=False)

TourRequestParams = TypedDict('TourRequestParams', {
    'session_id': Required['str'],
    'action': Required['str'],
    'surface': 'Union[str, None]',
    'selector': 'Union[str, None]',
    'title': 'Union[str, None]',
    'text': 'Union[str, None]',
    'side': 'Union[str, None]',
    'steps': 'Union[builtins.list[TourStep], None]',
    'step_index': 'Union[int, None]',
}, total=False)

TourStep = TypedDict('TourStep', {
    'selector': 'Union[str, None]',
    'title': 'Union[str, None]',
    'text': 'Union[str, None]',
    'side': 'Union[str, None]',
}, total=False)

TranscriptMessage = TypedDict('TranscriptMessage', {
    'role': Required['str'],
    'text': 'Union[str, None]',
    'timestamp': 'Union[float, None]',
    'row_id': 'Union[int, None]',
    'display_kind': 'Union[str, None]',
    'display_metadata': 'Union[Any, None]',
    'name': 'Union[str, None]',
    'context': 'Union[str, None]',
    'args': 'Union[dict[str, Any], None]',
    'reasoning': 'Union[str, None]',
}, total=False)

UiMetaConflict = TypedDict('UiMetaConflict', {
    'expected': 'Any',
    'actual': 'int',
}, total=False)

Usage = TypedDict('Usage', {
    'model': 'str',
    'input': 'int',
    'output': 'int',
    'reasoning': 'int',
    'prompt': 'int',
    'completion': 'int',
    'total': 'int',
    'calls': 'int',
    'compressions': 'Union[int, None]',
    'context_used': 'Union[int, None]',
    'context_max': 'Union[int, None]',
    'context_percent': 'Union[int, None]',
    'context_source': 'Union[str, None]',
    'context_estimated': 'Union[bool, None]',
    'cache_hit_pct': 'Union[int, None]',
    'cache_read': 'Union[int, None]',
    'cache_write': 'Union[int, None]',
    'avg_latency_s': 'Union[float, None]',
    'avg_tps': 'Union[float, None]',
    'active_subagents': 'Union[int, None]',
    'dev_credits_spent_micros': 'Union[int, None]',
    'cost_usd': 'Union[float, None]',
    'cost_status': 'Union[str, None]',
}, total=False)

UsageBar = TypedDict('UsageBar', {
    'kind': Required['UsageBarKind'],
    'remaining_display': Required['str'],
    'total_display': Required['str'],
    'spent_display': Required['str'],
    'pct_used': 'Union[int, None]',
    'fill_fraction': Required['float'],
}, total=False)

UsageModel = TypedDict('UsageModel', {
    'ok': 'Union[bool, None]',
    'available': Required['bool'],
    'status': 'Union[str, None]',
    'plan_name': 'Union[str, None]',
    'renews_at': 'Union[str, None]',
    'renews_display': 'Union[str, None]',
    'subscription_remaining_display': 'Union[str, None]',
    'topup_remaining_display': 'Union[str, None]',
    'total_spendable_display': 'Union[str, None]',
    'has_topup': 'Union[bool, None]',
    'plan_bar': 'Union[UsageBar, None]',
    'topup_bar': 'Union[UsageBar, None]',
}, total=False)

ValueResult = TypedDict('ValueResult', {
    'value': Required['str'],
}, total=False)

VaultAddParams = TypedDict('VaultAddParams', {
    'profile': 'Union[str, None]',
    'kind': 'Union[VaultKind, None]',
    'label': 'Union[str, None]',
    'origin': 'Union[str, None]',
    'secret': 'Union[dict[str, Any], None]',
}, total=False)

VaultAddResult = TypedDict('VaultAddResult', {
    'id': Required['str'],
}, total=False)

VaultCodeRequestParams = TypedDict('VaultCodeRequestParams', {
    'session_id': Required['str'],
    'site': 'Union[str, None]',
    'hint': 'Union[str, None]',
}, total=False)

VaultItem = TypedDict('VaultItem', {
    'id': Required['str'],
    'kind': Required['str'],
    'label': Required['str'],
    'origin': 'Union[str, None]',
    'created_at': 'str',
    'identifier': 'Union[str, None]',
    'identifier_type': 'Union[str, None]',
    'has_otp': 'Union[bool, None]',
    'backend': Required['str'],
}, total=False)

VaultListResult = TypedDict('VaultListResult', {
    'items': 'builtins.list[VaultItem]',
}, total=False)

VaultLockParams = TypedDict('VaultLockParams', {
    'profile': 'Union[str, None]',
    'name': 'Union[str, None]',
}, total=False)

VaultLockResult = TypedDict('VaultLockResult', {
    'locked': 'bool',
}, total=False)

VaultRemoveParams = TypedDict('VaultRemoveParams', {
    'profile': 'Union[str, None]',
    'id': 'Union[str, None]',
}, total=False)

VaultRemoveResult = TypedDict('VaultRemoveResult', {
    'removed': Required['bool'],
}, total=False)

VaultSaveLoginRequestParams = TypedDict('VaultSaveLoginRequestParams', {
    'session_id': Required['str'],
    'origin': Required['str'],
    'site': Required['str'],
}, total=False)

VaultSource = TypedDict('VaultSource', {
    'name': Required['str'],
    'display_name': Required['str'],
    'enabled': Required['bool'],
    'needs_unlock': Required['bool'],
    'unlocked': Required['bool'],
    'installed': Required['bool'],
}, total=False)

VaultSourceSetParams = TypedDict('VaultSourceSetParams', {
    'profile': 'Union[str, None]',
    'name': 'Union[str, None]',
    'enabled': 'Union[bool, None]',
}, total=False)

VaultSourceSetResult = TypedDict('VaultSourceSetResult', {
    'name': Required['str'],
    'enabled': Required['bool'],
}, total=False)

VaultSourcesResult = TypedDict('VaultSourcesResult', {
    'sources': 'builtins.list[VaultSource]',
}, total=False)

VaultUnlockParams = TypedDict('VaultUnlockParams', {
    'profile': 'Union[str, None]',
    'name': 'Union[str, None]',
    'password': 'Union[str, None]',
}, total=False)

VaultUnlockRequestParams = TypedDict('VaultUnlockRequestParams', {
    'session_id': Required['str'],
    'backend': Required['str'],
    'display_name': Required['str'],
}, total=False)

VaultUnlockResult = TypedDict('VaultUnlockResult', {
    'name': Required['str'],
    'unlocked': 'bool',
}, total=False)

VerificationEvidenceRow = TypedDict('VerificationEvidenceRow', {
    'id': 'Union[int, None]',
    'created_at': 'Union[str, None]',
    'session_id': 'Union[str, None]',
    'cwd': 'Union[str, None]',
    'root': 'Union[str, None]',
    'command': 'Union[str, None]',
    'canonical_command': 'Union[str, None]',
    'kind': 'Union[str, None]',
    'scope': 'Union[str, None]',
    'status': 'Union[str, None]',
    'exit_code': 'Union[int, None]',
    'output_summary': 'Union[str, None]',
}, total=False)

VerificationStatusInfo = TypedDict('VerificationStatusInfo', {
    'status': Required['str'],
    'evidence': 'Union[VerificationEvidenceRow, None]',
    'root': 'Union[str, None]',
    'session_id': 'Union[str, None]',
    'changed_paths': 'Union[builtins.list[str], None]',
}, total=False)

VerificationStatusParams = TypedDict('VerificationStatusParams', {
    'profile': 'Union[str, None]',
    'session_id': 'Union[str, None]',
    'session_key': 'Union[str, None]',
    'cwd': 'Union[str, None]',
}, total=False)

VerificationStatusResult = TypedDict('VerificationStatusResult', {
    'verification': Required['VerificationStatusInfo'],
}, total=False)

VoiceRecordParams = TypedDict('VoiceRecordParams', {
    'action': 'VoiceRecordAction',
    'session_id': 'Union[str, None]',
    'profile': 'Union[str, None]',
}, total=False)

VoiceRecordResult = TypedDict('VoiceRecordResult', {
    'status': Required['VoiceRecordStatus'],
    'reason': 'Union[str, None]',
}, total=False)

VoiceStatusPayload = TypedDict('VoiceStatusPayload', {
    'state': Required['str'],
}, total=False)

VoiceToggleParams = TypedDict('VoiceToggleParams', {
    'action': 'VoiceToggleAction',
    'profile': 'Union[str, None]',
}, total=False)

VoiceToggleResult = TypedDict('VoiceToggleResult', {
    'enabled': Required['bool'],
    'record_key': Required['str'],
    'tts': Required['bool'],
    'stop_hint': 'Union[str, None]',
    'available': 'Union[bool, None]',
    'audio_available': 'Union[bool, None]',
    'stt_available': 'Union[bool, None]',
    'details': 'Union[str, None]',
}, total=False)

VoiceTranscriptPayload = TypedDict('VoiceTranscriptPayload', {
    'text': 'Union[str, None]',
    'stop_phrase': 'Union[bool, None]',
    'typed': 'Union[bool, None]',
    'no_speech_limit': 'Union[bool, None]',
}, total=False)

VoiceTtsParams = TypedDict('VoiceTtsParams', {
    'text': Required['str'],
    'profile': 'Union[str, None]',
}, total=False)

VoiceTtsResult = TypedDict('VoiceTtsResult', {
    'status': Required['str'],
}, total=False)

WaitBarrierTarget = TypedDict('WaitBarrierTarget', {
    'type': Required["Literal['session', 'pid']"],
    'target': Required['Union[str, int]'],
    'reason': 'str',
}, total=False)

WaitBarrierUntil = TypedDict('WaitBarrierUntil', {
    'type': Required["Literal['until']"],
    'until_at': Required['float'],
    'reason': 'str',
}, total=False)

WakeControlParams = TypedDict('WakeControlParams', {
    'profile': 'Union[str, None]',
}, total=False)

WakeDetectedPayload = TypedDict('WakeDetectedPayload', {
    'phrase': Required['str'],
    'profile': 'Union[str, None]',
    'start_new_session': Required['bool'],
}, total=False)

WakeFeedParams = TypedDict('WakeFeedParams', {
    'pcm': 'Union[str, None]',
    'pcm_b64': 'Union[str, None]',
    'sample_rate': 'Union[int, None]',
    'profile': 'Union[str, None]',
}, total=False)

WakeFeedResult = TypedDict('WakeFeedResult', {
    'reason': 'Union[str, None]',
    'fed': Required['bool'],
}, total=False)

WakeInputDevice = TypedDict('WakeInputDevice', {
    'selector': 'Union[int, str, None]',
    'name': 'Union[str, None]',
    'error': 'Union[str, None]',
    'max_input_channels': 'Union[int, None]',
    'default_samplerate': 'Union[float, None]',
    'hostapi_index': 'Union[int, None]',
    'hostapi': 'Union[str, None]',
}, total=False)

WakePauseResult = TypedDict('WakePauseResult', {
    'reason': 'Union[str, None]',
    'paused': Required['bool'],
}, total=False)

WakeResumeResult = TypedDict('WakeResumeResult', {
    'reason': 'Union[str, None]',
    'resumed': Required['bool'],
}, total=False)

WakeStartParams = TypedDict('WakeStartParams', {
    'surface': 'Union[str, None]',
    'persist': 'Union[bool, None]',
    'client_capture': 'Union[bool, None]',
    'session_id': 'Union[str, None]',
    'profile': 'Union[str, None]',
}, total=False)

WakeStartResult = TypedDict('WakeStartResult', {
    'started': Required['bool'],
    'reason': 'Union[str, None]',
    'hint': 'Union[str, None]',
    'phrase': 'Union[str, None]',
    'provider': 'Union[str, None]',
    'owner_surface': 'Union[str, None]',
    'enabled_persisted': 'Union[bool, None]',
    'capture': 'Union[str, None]',
    'sample_rate': 'Union[int, None]',
    'frame_length': 'Union[int, None]',
}, total=False)

WakeStatusParams = TypedDict('WakeStatusParams', {
    'surface': 'Union[str, None]',
    'client_capture': 'Union[bool, None]',
    'profile': 'Union[str, None]',
}, total=False)

WakeStatusResult = TypedDict('WakeStatusResult', {
    'listening': Required['bool'],
    'owned_by_caller': Required['bool'],
    'owner_surface': 'Union[str, None]',
    'phrase': Required['str'],
    'provider': Required['str'],
    'configured_surface': Required['str'],
    'input_device': Required['WakeInputDevice'],
    'available': Required['bool'],
    'hint': Required['str'],
    'enabled': Required['bool'],
    'audio_silent': Required['bool'],
    'capture': Required['str'],
    'local_input_available': Required['bool'],
    'sample_rate': Required['int'],
    'frame_length': Required['int'],
}, total=False)

WakeStopParams = TypedDict('WakeStopParams', {
    'persist': 'Union[bool, None]',
    'profile': 'Union[str, None]',
}, total=False)

WakeStopResult = TypedDict('WakeStopResult', {
    'reason': 'Union[str, None]',
    'stopped': Required['bool'],
    'disabled_persisted': Required['bool'],
}, total=False)

_SessionScoped = TypedDict('_SessionScoped', {
    'session_id': 'Union[str, None]',
}, total=False)

ApprovalChoice: TypeAlias = Literal['once', 'session', 'always', 'deny']

ArgumentMode: TypeAlias = Literal['options', 'text', 'mixed']

AutoReloadCardKind: TypeAlias = Literal['canonical', 'distinct', 'none']

BatteryCategory: TypeAlias = Literal['good', 'warn', 'bad', 'critical', 'dim']

BrowserAction: TypeAlias = Literal['status', 'connect', 'disconnect']

ClarifyLockStatus: TypeAlias = Literal['ok', 'expired']

ConnectionActor: TypeAlias = Literal['user', 'backend_watcher', 'clock']

ConnectionAnswerStatus: TypeAlias = Literal['approved', 'skipped']

ConnectionSettleReason: TypeAlias = Literal['all_resolved', 'continue', 'deadline', 'interrupt', 'unavailable']

ConnectionTargetAction: TypeAlias = Literal['authorize', 'connect', 'enable', 'install', 'reconnect']

ConnectionTargetKind: TypeAlias = Literal['connector', 'mcp']

ConnectionTargetState: TypeAlias = Literal['pending', 'initiated', 'connected', 'skipped', 'failed', 'expired', 'unavailable', 'not_connected']

CorrectionStatus: TypeAlias = Literal['queued', 'redirected', 'rejected']

CronAction: TypeAlias = Literal['list', 'add', 'remove', 'pause', 'resume']

DispatchType: TypeAlias = Literal['exec', 'alias', 'plugin', 'send', 'skill', 'prefill']

ForeignSource: TypeAlias = Literal['claude', 'codex']

InterruptStatus: TypeAlias = Literal['interrupted', 'not_interrupted']

LiveSessionStatus: TypeAlias = Literal['idle', 'starting', 'waiting', 'working', 'streaming', 'resuming']

McpOauthPollStatus: TypeAlias = Literal['pending', 'approved', 'error']

McpRuntimeStatus: TypeAlias = Literal['connected', 'disabled', 'connecting', 'failed', 'lazy', 'configured']

PaymentMethodKind: TypeAlias = Literal['card', 'link', 'unknown']

PluginsAction: TypeAlias = Literal['list', 'toggle', 'install', 'update', 'remove']

ProcessKillStatus: TypeAlias = Literal['killed', 'already_exited', 'not_found', 'error']

PromptSubmitStatus: TypeAlias = Literal['streaming', 'queued', 'steered', 'redirected']

ReactionAuthor: TypeAlias = Literal['user', 'agent']

ReloadMcpStatus: TypeAlias = Literal['confirm_required', 'reloaded']

ResumePhaseStatus: TypeAlias = Literal['loading', 'complete', 'failed']

SkillsAction: TypeAlias = Literal['list', 'search', 'install', 'browse', 'inspect']

SteerStatus: TypeAlias = Literal['queued', 'rejected']

SubagentStatus: TypeAlias = Literal['queued', 'running', 'completed', 'failed', 'error', 'timeout', 'interrupted']

SubscriptionChangeEffect: TypeAlias = Literal['charge_now', 'scheduled', 'no_op', 'blocked']

SubscriptionContext: TypeAlias = Literal['personal', 'team']

ToolsAction: TypeAlias = Literal['enable', 'disable']

TurnStatus: TypeAlias = Literal['complete', 'error', 'interrupted']

UsageBarKind: TypeAlias = Literal['plan', 'topup']

VaultKind: TypeAlias = Literal['login', 'payment', 'address']

VoiceRecordAction: TypeAlias = Literal['start', 'stop']

VoiceRecordStatus: TypeAlias = Literal['recording', 'stopped', 'busy']

VoiceToggleAction: TypeAlias = Literal['status', 'on', 'off', 'tts']
