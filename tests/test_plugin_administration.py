import pytest

from edith_hermes.plugin_administration import AsyncPluginAdministration


@pytest.mark.asyncio
async def test_plugin_review_change_and_receipt_use_exact_profile_and_no_replay():
    calls = []
    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('.change'):
                raise TimeoutError('Unknown native publication outcome')
            return {'id': 'review', 'profileId': 'door'}
    client = AsyncPluginAdministration(Transport(), profile='door')
    await client.review('user:notes', 'update')
    assert calls[-1][1] == dict(profile='door', resource='user:notes', kind='update', enabled=None, timeout=120)
    with pytest.raises(TimeoutError):
        await client.change('user:notes', 'update', review_id='review', digest='exact', request_id='once', accepted=True)
    assert len(calls) == 2
    await client.operation('once')
    assert calls[-1] == ('edith.desktop.v1.pluginAdministration.operation', dict(profile='door', request_id='once'))
    with pytest.raises(ValueError):
        AsyncPluginAdministration(Transport(), profile='all')
