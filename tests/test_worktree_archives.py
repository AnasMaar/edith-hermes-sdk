import pytest

from edith_hermes.worktree_archives import AsyncWorktreeArchives


@pytest.mark.asyncio
async def test_preservation_scopes_and_reconciles_without_repeating_a_move():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('.mutate'):
                raise TimeoutError('The move may have completed')
            return {'status': 'applied'}

    client = AsyncWorktreeArchives(Transport(), profile='family')
    with pytest.raises(TimeoutError):
        await client.mutate('C:/repo', 'C:/repo/linked', revision='one', request_id='once', kind='archive')
    assert (await client.operation('C:/repo', 'once'))['status'] == 'applied'
    assert len(calls) == 2
    assert calls[0][1]['profile'] == 'family'
    assert calls[1][1] == {'repository': 'C:/repo', 'request_id': 'once', 'profile': 'family'}
    with pytest.raises(ValueError):
        AsyncWorktreeArchives(Transport(), profile='all')
