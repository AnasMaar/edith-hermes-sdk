import pytest

from edith_hermes.memory_backends import AsyncMemoryBackends


@pytest.mark.asyncio
async def test_concrete_profile_is_preserved_for_config_and_one_native_setup_receipt():
    class Transport:
        def __init__(self):
            self.calls = []

        async def call(self, method, **params):
            self.calls.append((method, params))
            return {'id': 'once', 'status': 'running'}

    transport = Transport()
    client = AsyncMemoryBackends(transport, profile='door')
    await client.inventory()
    await client.schema('honcho', surface='declared')
    await client.change('honcho', 'setup', revision='checked', request_id='once', confirmed=True)
    await client.operation('once')
    assert all(params['profile'] == 'door' for _, params in transport.calls)
    assert transport.calls[2][1]['request_id'] == transport.calls[3][1]['request_id'] == 'once'
    assert transport.calls[2][1]['confirmed'] is True
    with pytest.raises(ValueError):
        AsyncMemoryBackends(transport, profile='all')
