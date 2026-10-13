import pytest

from edith_hermes.integration_mutations import AsyncIntegrationMutations


@pytest.mark.asyncio
async def test_mcp_removal_is_revision_checked_profile_scoped_and_never_dispatch_retries():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('remove'):
                raise TimeoutError('Native save completed, reply lost')
            return {'requestId': 'once', 'name': 'calendar', 'status': 'applied', 'revision': 'removed'}

    service = AsyncIntegrationMutations(Connection(), profile='door')
    with pytest.raises(TimeoutError):
        await service.remove_mcp('calendar', revision='actual-config', request_id='once')
    assert (await service.operation('once'))['status'] == 'applied'
    assert calls == [
        ('edith.desktop.v1.mcp.remove', {'profile': 'door', 'name': 'calendar', 'revision': 'actual-config', 'request_id': 'once'}),
        ('edith.desktop.v1.mcp.operation', {'profile': 'door', 'request_id': 'once'}),
    ]
