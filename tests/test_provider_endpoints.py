import pytest

from edith_hermes.provider_endpoints import AsyncProviderEndpoints


@pytest.mark.asyncio
async def test_endpoints_use_narrow_changes_with_native_scope_and_no_automatic_replay():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('.change'):
                raise TimeoutError('Native effect may already be applied')
            return dict(profileId='family', revision='one', endpoints=[])

    client = AsyncProviderEndpoints(Transport(), profile='family')
    await client.inventory()
    with pytest.raises(TimeoutError):
        await client.change('local-provider', revision='one', request_id='once', kind='save', changes={'model': 'new-model'})
    assert len(calls) == 2 and calls[-1][1]['changes'] == {'model': 'new-model'}
    await client.operation('once')
    await client.test('local-provider', {})
    assert calls[-1][1] == dict(profile='family', id='local-provider', changes={}, timeout=180)
    with pytest.raises(ValueError):
        AsyncProviderEndpoints(Transport(), profile='all')
