import pytest

from edith_hermes.file_mutations import AsyncFileMutations


@pytest.mark.asyncio
async def test_mutations_pin_profile_workspace_revisions_and_nonce_without_retry():
    calls = []

    class RPC:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('.mutate'):
                raise TimeoutError('Unknown publication')
            return {}

    sdk = AsyncFileMutations(RPC(), profile='door')
    await sdk.inspect('C:/workspace/a', workspace_root='C:/workspace')
    with pytest.raises(TimeoutError):
        await sdk.mutate('copy', workspace_root='C:/workspace', request_id='one', payload={'sourcePath': 'C:/workspace/a', 'destinationPath': 'C:/workspace/b', 'sourceRevision': 'source', 'revision': 'missing'})
    await sdk.operation('one')
    assert len(calls) == 3 and all(params['profile'] == 'door' for _, params in calls)
    assert calls[1][1]['workspace_root'] == 'C:/workspace' and calls[1][1]['payload']['sourceRevision'] == 'source'
    with pytest.raises(ValueError):
        AsyncFileMutations(RPC(), profile='all')
