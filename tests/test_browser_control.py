from typing import Any

import pytest

from edith_hermes.browser_control import AsyncBrowserControl


class Caller:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def call(self, method: str, **params: Any) -> Any:
        self.calls.append((method, params))
        return {'accepted': True}


@pytest.mark.asyncio
async def test_browser_commands_keep_exact_session_and_local_lease() -> None:
    caller = Caller()
    sdk = AsyncBrowserControl(caller, 'door')
    await sdk.register(session_id='native-session', lease_id='owned-lease', controller_id='desktop', browser_profile_id='isolated-browser', capabilities=['browser_snapshot'])
    await sdk.result(session_id='native-session', lease_id='owned-lease', command_id='once', ok=False, error='Navigation ended', result={'untrusted': 'discard'})
    assert caller.calls[0] == ('edith.desktop.v1.browser-controller.register', {'profile':'door','session_id': 'native-session', 'lease_id': 'owned-lease', 'controller_id': 'desktop', 'browser_profile_id': 'isolated-browser', 'capabilities': ['browser_snapshot'], 'protocol_version': 1})
    assert caller.calls[1][1] == {'profile':'door','session_id': 'native-session', 'lease_id': 'owned-lease', 'command_id': 'once', 'ok': False, 'result': None, 'error': 'Navigation ended'}
    await sdk.heartbeat(session_id='native-session', lease_id='owned-lease')
    await sdk.detach(session_id='native-session', lease_id='owned-lease')
    assert all(params['profile']=='door' and params['session_id'] == 'native-session' and params['lease_id'] == 'owned-lease' for _, params in caller.calls)


@pytest.mark.asyncio
async def test_browser_feature_configuration_requires_the_captured_revision() -> None:
    caller = Caller()
    sdk = AsyncBrowserControl(caller)
    await sdk.settings()
    await sdk.configure(enabled=True, revision='captured-native-config')
    assert caller.calls == [('edith.desktop.v1.browser-controller.settings', {'profile':'default'}), ('edith.desktop.v1.browser-controller.configure', {'profile':'default','enabled': True, 'revision': 'captured-native-config'})]
