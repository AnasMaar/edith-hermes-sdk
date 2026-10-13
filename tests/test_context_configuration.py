import pytest

from edith_hermes.context_configuration import AsyncContextConfiguration


@pytest.mark.asyncio
async def test_context_defaults_send_one_narrow_change_with_profile_revision_and_receipt():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('.change'):
                raise TimeoutError('Native save may be accepted')
            return dict(profileId='family', revision='one', fields=[])

    api = AsyncContextConfiguration(Transport(), profile='family')
    assert (await api.inventory())['profileId'] == 'family'
    with pytest.raises(TimeoutError):
        await api.change(revision='one', request_id='same', changes={'compression.threshold_tokens': None})
    assert len(calls) == 2 and calls[-1][1]['changes'] == {'compression.threshold_tokens': None}
    await api.operation('same')
    assert calls[-1][1] == {'profile': 'family', 'request_id': 'same'}
    with pytest.raises(ValueError):
        AsyncContextConfiguration(Transport(), profile='all')
