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


@pytest.mark.asyncio
async def test_cron_edit_snapshot_and_receipt_keep_exact_owner_and_request():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('snapshot'):
                return {'jobs': [{'job': {'id': 'job'}, 'revision': 'v1'}]}
            return {'requestId': 'edit', 'profileId': 'door', 'jobId': 'job', 'revision': 'v2', 'status': 'applied'}

    service = AsyncScheduleMutations(Connection(), profile='door')
    assert (await service.snapshot())[0]['revision'] == 'v1'
    assert (await service.edit('job', revision='v1', updates={'name': 'Changed'}, request_id='edit'))['status'] == 'applied'
    assert (await service.edit_operation('edit'))['revision'] == 'v2'
    assert calls == [
        ('edith.desktop.v1.cron.snapshot', {'profile': 'door'}),
        ('edith.desktop.v1.cron.edit', {'profile': 'door', 'job_id': 'job', 'revision': 'v1', 'updates': {'name': 'Changed'}, 'request_id': 'edit', 'timeout': 60}),
        ('edith.desktop.v1.cron.editOperation', {'profile': 'door', 'request_id': 'edit'}),
    ]
