import pytest

from edith_hermes.command_actions import AsyncCommandActions


@pytest.mark.asyncio
async def test_native_diagnostics_keep_exact_profile_action_and_receipt():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return {}

    sdk = AsyncCommandActions(Connection(), profile='door')
    await sdk.capabilities()
    await sdk.start(request_id='same-request', action='doctor')
    await sdk.operation('same-request')
    assert calls == [
        ('edith.desktop.v1.command-actions.capabilities', {'profile':'door'}),
        ('edith.desktop.v1.command-actions.start', {'profile':'door','request_id':'same-request','action':'doctor'}),
        ('edith.desktop.v1.command-actions.operation', {'profile':'door','request_id':'same-request'})]


@pytest.mark.asyncio
async def test_explicit_native_gateway_action_preserves_profile_and_nonce():
    calls = []

    class RPC:
        async def call(self, method, **params):
            calls.append((method, params))
            return {}

    await AsyncCommandActions(RPC(), profile='door').start(request_id='gateway-once', action='gateway-start')
    assert calls == [('edith.desktop.v1.command-actions.start', {'profile': 'door', 'request_id': 'gateway-once', 'action': 'gateway-start'})]
