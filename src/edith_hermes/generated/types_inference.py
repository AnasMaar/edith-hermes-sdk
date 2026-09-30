"""Generated wire-shape types; required keys are explicit. Do not edit."""
from __future__ import annotations
import builtins
from typing import Any, Literal, Union
from typing_extensions import Required, TypedDict, TypeAlias
from . import types_control_plane
from . import types_images
from . import types_runtime
from . import types_tools
from . import types_native

HTTPValidationError = TypedDict('HTTPValidationError', {
    'detail': 'builtins.list[ValidationError]',
}, total=False)

ValidationError = TypedDict('ValidationError', {
    'loc': Required['builtins.list[Union[str, int]]'],
    'msg': Required['str'],
    'type': Required['str'],
}, total=False)

createChatCompletionMessagesItem = TypedDict('createChatCompletionMessagesItem', {
    'role': Required["Literal['system', 'user', 'assistant']"],
    'content': Required['str'],
}, total=False)

createChatCompletionResult = TypedDict('createChatCompletionResult', {
    'id': 'str',
    'object': 'str',
    'created': 'int',
    'model': 'str',
    'choices': 'builtins.list[createChatCompletionResultChoicesItem]',
}, total=False)

createChatCompletionResultChoicesItem = TypedDict('createChatCompletionResultChoicesItem', {
    'index': 'int',
    'message': 'createChatCompletionResultChoicesItemMessage',
    'finish_reason': 'str',
}, total=False)

createChatCompletionResultChoicesItemMessage = TypedDict('createChatCompletionResultChoicesItemMessage', {
    'role': 'str',
    'content': 'str',
}, total=False)

createCompletionResult = TypedDict('createCompletionResult', {
    'id': 'str',
    'object': 'str',
    'created': 'int',
    'model': 'str',
    'choices': 'builtins.list[createCompletionResultChoicesItem]',
}, total=False)

createCompletionResultChoicesItem = TypedDict('createCompletionResultChoicesItem', {
    'text': 'str',
    'index': 'int',
    'logprobs': 'Union[dict[str, Any], None]',
    'finish_reason': 'str',
}, total=False)
