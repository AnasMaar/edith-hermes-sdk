"""Generated wire-shape types; required keys are explicit. Do not edit."""
from __future__ import annotations
import builtins
from typing import Any, Literal, Union
from typing_extensions import Required, TypedDict, TypeAlias
from . import types_control_plane
from . import types_images
from . import types_runtime
from . import types_tools
from . import types_inference
from . import types_native

CredentialStatus = TypedDict('CredentialStatus', {
    'state': Required["Literal['authenticated', 'unauthenticated', 'expired', 'revoked', 'unknown']"],
    'loggedIn': Required['bool'],
    'validity': Required["Literal['unknown', 'expired', 'revoked']"],
    'expiresAt': 'Union[str, None]',
    'hasRefreshToken': 'bool',
    'source': 'Union[str, None]',
}, total=False)

AuthProvider = TypedDict('AuthProvider', {
    'id': Required['str'],
    'name': Required['str'],
    'flow': Required['str'],
    'loginSupported': Required['bool'],
    'disconnectSupported': Required['bool'],
    'cliCommand': 'Union[str, None]',
    'docsUrl': 'Union[str, None]',
    'status': Required['CredentialStatus'],
}, total=False)

ProviderLogin = TypedDict('ProviderLogin', {
    'id': Required['str'],
    'instanceId': Required['str'],
    'profileId': Required['str'],
    'providerId': Required['str'],
    'flow': Required['str'],
    'status': Required["Literal['pending', 'approved', 'denied', 'expired', 'cancelled', 'failed']"],
    'verificationUrl': Required['Union[str, None]'],
    'userCode': Required['Union[str, None]'],
    'expiresAt': Required['Union[str, None]'],
    'pollInterval': Required['float'],
    'errorCode': Required["Literal[None, 'authorization_denied', 'authorization_expired', 'authorization_failed', 'runtime_session_lost', 'cancelled']"],
}, total=False)

ProviderAccount = TypedDict('ProviderAccount', {
    'id': Required['str'],
    'index': Required['int'],
    'providerId': Required['str'],
    'label': Required['str'],
    'authType': Required['str'],
    'source': Required['str'],
    'priority': Required['int'],
    'requestCount': Required['int'],
    'hasRefreshToken': Required['bool'],
    'lastStatus': 'Union[int, None]',
    'validity': Required["Literal['unknown', 'expired', 'revoked']"],
}, total=False)

AuthMutation = TypedDict('AuthMutation', {
    'ok': Required['bool'],
    'providerId': Required['str'],
    'count': 'int',
}, total=False)

listAuthProvidersResult = TypedDict('listAuthProvidersResult', {
    'items': Required['builtins.list[AuthProvider]'],
}, total=False)

listProviderAccountsResult = TypedDict('listProviderAccountsResult', {
    'items': Required['builtins.list[ProviderAccount]'],
}, total=False)
