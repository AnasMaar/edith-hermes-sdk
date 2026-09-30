"""Generated wire-shape types; required keys are explicit. Do not edit."""
from __future__ import annotations
import builtins
from typing import Any, Literal, Union
from typing_extensions import Required, TypedDict, TypeAlias
from . import types_control_plane
from . import types_images
from . import types_runtime
from . import types_providers
from . import types_inference
from . import types_native

ToolDefinition = TypedDict('ToolDefinition', {
    'name': Required['str'],
    'description': Required['str'],
    'inputSchema': Required['dict[str, Any]'],
    'outputSchema': 'dict[str, Any]',
    'annotations': 'dict[str, Any]',
}, total=False)

ToolBundle = TypedDict('ToolBundle', {
    'id': Required['str'],
    'name': Required['str'],
    'description': 'str',
    'transport': Required["Literal['callback', 'mcp']"],
    'callback': 'CallbackTransport',
    'mcpServerId': 'str',
    'tools': Required['builtins.list[ToolDefinition]'],
    'createdAt': Required['str'],
    'updatedAt': 'str',
}, total=False)

CreateToolBundleRequest = TypedDict('CreateToolBundleRequest', {
    'name': Required['str'],
    'description': 'str',
    'transport': Required["Literal['callback', 'mcp']"],
    'callback': 'CallbackTransport',
    'mcpServerId': 'str',
    'tools': 'builtins.list[ToolDefinition]',
}, total=False)

CallbackTransport = TypedDict('CallbackTransport', {
    'url': Required['str'],
    'timeoutSeconds': 'int',
    'secretRef': 'str',
}, total=False)

BindingScope0 = TypedDict('BindingScope0', {
    'level': Required["Literal['instance']"],
    'instanceId': Required['str'],
}, total=False)

BindingScope1 = TypedDict('BindingScope1', {
    'level': Required["Literal['profile']"],
    'instanceId': Required['str'],
    'profileId': Required['str'],
}, total=False)

BindingScope2 = TypedDict('BindingScope2', {
    'level': Required["Literal['session']"],
    'instanceId': Required['str'],
    'profileId': Required['str'],
    'sessionId': Required['str'],
}, total=False)

CreateToolBindingRequest = TypedDict('CreateToolBindingRequest', {
    'bundleId': Required['str'],
    'scope': Required['BindingScope'],
    'enabledTools': 'builtins.list[str]',
    'approvalPolicy': "Literal['always', 'on_dangerous', 'never']",
    'priority': 'int',
}, total=False)

ToolBinding = TypedDict('ToolBinding', {
    'bundleId': Required['str'],
    'scope': Required['BindingScope'],
    'enabledTools': 'builtins.list[str]',
    'approvalPolicy': "Literal['always', 'on_dangerous', 'never']",
    'priority': 'int',
    'id': Required['str'],
    'status': Required["Literal['pending', 'active', 'degraded', 'failed']"],
    'nativeServerName': 'str',
    'nativeState': 'dict[str, Any]',
    'error': 'str',
    'createdAt': Required['str'],
}, total=False)

McpServer = TypedDict('McpServer', {
    'name': Required['str'],
    'transport': Required["Literal['stdio', 'streamable_http', 'sse']"],
    'command': 'str',
    'args': 'builtins.list[str]',
    'url': 'str',
    'headers': 'dict[str, str]',
    'auth': "Literal['oauth']",
    'environment': 'dict[str, str]',
    'secretRefs': 'dict[str, str]',
    'id': Required['str'],
    'status': Required["Literal['unknown', 'connecting', 'ready', 'needs_auth', 'failed']"],
    'discoveredTools': 'builtins.list[ToolDefinition]',
    'createdAt': Required['str'],
}, total=False)

CreateMcpServerRequest = TypedDict('CreateMcpServerRequest', {
    'name': Required['str'],
    'transport': Required["Literal['stdio', 'streamable_http', 'sse']"],
    'command': 'str',
    'args': 'builtins.list[str]',
    'url': 'str',
    'headers': 'dict[str, str]',
    'auth': "Literal['oauth']",
    'environment': 'dict[str, str]',
    'secretRefs': 'dict[str, str]',
}, total=False)

ToolCallRequest = TypedDict('ToolCallRequest', {
    'callId': Required['str'],
    'tool': Required['str'],
    'arguments': Required['dict[str, Any]'],
    'target': Required['BindingScope'],
    'deadline': 'str',
    'metadata': 'dict[str, Any]',
}, total=False)

ToolCallResult = TypedDict('ToolCallResult', {
    'callId': Required['str'],
    'isError': Required['bool'],
    'content': Required['builtins.list[ToolCallResultContentItem]'],
    'structuredContent': 'Any',
}, total=False)

ToolCallResultContentItem = TypedDict('ToolCallResultContentItem', {
    'type': Required["Literal['text', 'image', 'resource', 'json']"],
    'text': 'str',
    'data': 'Any',
}, total=False)

Problem = TypedDict('Problem', {
    'type': Required['str'],
    'title': Required['str'],
    'status': Required['int'],
    'detail': 'str',
    'traceId': 'str',
}, total=False)

listToolBundlesResult = TypedDict('listToolBundlesResult', {
    'items': Required['builtins.list[ToolBundle]'],
}, total=False)

listToolBindingsResult = TypedDict('listToolBindingsResult', {
    'items': Required['builtins.list[ToolBinding]'],
}, total=False)

listMcpServersResult = TypedDict('listMcpServersResult', {
    'items': Required['builtins.list[McpServer]'],
}, total=False)

BindingScope: TypeAlias = Union[BindingScope0, BindingScope1, BindingScope2]
