import pytest

from edith_hermes.schedule_mutations import AsyncScheduleMutations


@pytest.mark.asyncio
async def test_cron_creation_is_scoped_and_reconciles_without_dispatch_replay():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('create'):
                raise TimeoutError('Native creation reply lost')
            return {'requestId': 'once', 'profileId': 'door', 'status': 'applied', 'jobId': 'native-job'}

    service = AsyncScheduleMutations(Connection(), profile='door')
    options = {'schedule': 'every 2h', 'name': 'Notes', 'prompt': 'Read notes', 'paused': True}
    with pytest.raises(TimeoutError):
        await service.create(options, request_id='once')
    assert (await service.operation('once'))['jobId'] == 'native-job'
    assert calls == [
        ('edith.desktop.v1.cron.create', {'profile': 'door', 'options': options, 'request_id': 'once', 'timeout': 60}),
        ('edith.desktop.v1.cron.creation', {'profile': 'door', 'request_id': 'once'}),
    ]
