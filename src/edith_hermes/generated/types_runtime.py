"""Generated wire-shape types; required keys are explicit. Do not edit."""
from __future__ import annotations
import builtins
from typing import Any, Literal, Union
from typing_extensions import Required, TypedDict, TypeAlias
from . import types_control_plane
from . import types_images
from . import types_tools
from . import types_providers
from . import types_inference
from . import types_native

RuntimeCapabilities = TypedDict('RuntimeCapabilities', {
    'facadeVersion': Required['str'],
    'upstreamContract': Required['str'],
    'upstreamRevision': 'str',
    'transports': Required["builtins.list[Literal['http', 'sse', 'websocket', 'json_rpc']]"],
    'nativeMethods': Required['builtins.list[str]'],
    'notifications': 'builtins.list[str]',
    'serverRequests': 'builtins.list[str]',
    'extensions': 'dict[str, Any]',
}, total=False)

Session = TypedDict('Session', {
    'id': Required['str'],
    'instanceId': Required['str'],
    'profileId': Required['str'],
    'title': 'str',
    'status': Required["Literal['creating', 'idle', 'running', 'waiting_for_input', 'interrupted', 'closed', 'failed']"],
    'nativeSessionId': 'str',
    'metadata': 'dict[str, Any]',
    'createdAt': Required['str'],
    'updatedAt': 'str',
}, total=False)

SessionPage = TypedDict('SessionPage', {
    'items': Required['builtins.list[Session]'],
    'nextCursor': 'Union[str, None]',
}, total=False)

CreateSessionRequest = TypedDict('CreateSessionRequest', {
    'title': 'str',
    'resumeNativeSessionId': 'str',
    'workingDirectory': 'str',
    'environment': 'dict[str, str]',
    'metadata': 'dict[str, Any]',
    'toolBindingIds': 'builtins.list[str]',
}, total=False)

SessionAction0 = TypedDict('SessionAction0', {
    'type': Required["Literal['resume', 'activate', 'close', 'interrupt', 'compress', 'undo']"],
}, total=False)

SessionAction1 = TypedDict('SessionAction1', {
    'type': Required["Literal['branch']"],
    'fromTurnId': 'str',
}, total=False)

ContentPart0 = TypedDict('ContentPart0', {
    'type': Required["Literal['text']"],
    'text': Required['str'],
}, total=False)

ContentPart1 = TypedDict('ContentPart1', {
    'type': Required["Literal['image', 'file']"],
    'url': Required['str'],
    'mediaType': 'str',
}, total=False)

SubmitTurnRequest = TypedDict('SubmitTurnRequest', {
    'content': Required['Union[str, builtins.list[ContentPart]]'],
    'mode': "Literal['enqueue', 'steer']",
    'toolBindingIds': 'builtins.list[str]',
    'metadata': 'dict[str, Any]',
}, total=False)

Turn = TypedDict('Turn', {
    'id': Required['str'],
    'sessionId': Required['str'],
    'status': Required["Literal['queued', 'running', 'waiting_for_approval', 'completed', 'stopped', 'failed']"],
    'output': 'builtins.list[ContentPart]',
    'error': 'Union[Problem, None]',
    'createdAt': Required['str'],
    'completedAt': 'Union[str, None]',
}, total=False)

TurnAction0 = TypedDict('TurnAction0', {
    'type': Required["Literal['stop']"],
}, total=False)

TurnAction1 = TypedDict('TurnAction1', {
    'type': Required["Literal['steer']"],
    'content': Required['str'],
}, total=False)

TurnAction2 = TypedDict('TurnAction2', {
    'type': Required["Literal['approval']"],
    'requestId': Required['str'],
    'decision': Required["Literal['allow_once', 'allow_session', 'deny']"],
}, total=False)

RuntimeEvent = TypedDict('RuntimeEvent', {
    'id': Required['str'],
    'type': Required['str'],
    'occurredAt': Required['str'],
    'nativeMethod': 'str',
    'data': Required['Any'],
}, total=False)

JsonRpcRequest = TypedDict('JsonRpcRequest', {
    'jsonrpc': Required["Literal['2.0']"],
    'id': 'Union[str, int, None]',
    'method': Required['str'],
    'params': 'Union[dict[str, Any], builtins.list[Any]]',
}, total=False)

JsonRpcResponse = TypedDict('JsonRpcResponse', {
    'jsonrpc': Required["Literal['2.0']"],
    'id': 'Union[str, int, None]',
    'result': 'Any',
    'error': 'JsonRpcResponseError',
}, total=False)

JsonRpcResponseError = TypedDict('JsonRpcResponseError', {
    'code': Required['int'],
    'message': Required['str'],
    'data': 'Any',
}, total=False)

Problem = TypedDict('Problem', {
    'type': Required['str'],
    'title': Required['str'],
    'status': Required['int'],
    'detail': 'str',
    'traceId': 'str',
}, total=False)

SessionAction: TypeAlias = Union[SessionAction0, SessionAction1]

ContentPart: TypeAlias = Union[ContentPart0, ContentPart1]

TurnAction: TypeAlias = Union[TurnAction0, TurnAction1, TurnAction2]
