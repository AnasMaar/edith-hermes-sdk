import pytest

from edith_hermes.channel_pairings import AsyncChannelPairings


@pytest.mark.asyncio
async def test_pairings_keep_profile_and_receipt_identity_without_retrying_authentication():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('.start'):
                raise TimeoutError('Pairing may be accepted')
            return dict(id='flow', platform='telegram', profileId='family', status='waiting')

    api = AsyncChannelPairings(Transport(), profile='family')
    with pytest.raises(TimeoutError):
        await api.start('telegram', request_id='flow')
    assert len(calls) == 1
    assert (await api.poll('flow'))['id'] == 'flow'
    await api.apply('flow', revision='one', apply_request_id='apply', allowed_users=['123'])
    assert calls[-1][1] == dict(profile='family', request_id='flow', revision='one', apply_request_id='apply', allowed_users=['123'], timeout=180)
    await api.cancel('flow')
    assert calls[-1][0].endswith('.cancel')
    with pytest.raises(ValueError):
        AsyncChannelPairings(Transport(), profile='all')
