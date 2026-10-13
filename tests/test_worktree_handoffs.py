import pytest

from edith_hermes.worktree_handoffs import AsyncWorktreeHandoffs, HandoffArguments


@pytest.mark.asyncio
async def test_handoff_reads_receipt_after_lost_mutation_and_binds_exact_session():
    calls = []
    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('.mutate'):
                raise TimeoutError('lost answer')
            return {'status': 'applied'}
    sdk = AsyncWorktreeHandoffs(Transport(), profile='family')
    args: HandoffArguments = dict(repository='C:/repo', source='C:/repo', target='C:/linked',
        source_revision='source', target_revision='target', source_branch='main', target_branch='moved', preserve_target=False)
    with pytest.raises(TimeoutError):
        await sdk.mutate(args, request_id='move-once')
    assert (await sdk.operation('C:/repo', 'move-once'))['status'] == 'applied'
    await sdk.bind('C:/repo', 'move-once', 'stored-session')
    assert [name.rsplit('.', 1)[1] for name, _ in calls] == ['mutate', 'operation', 'bind']
    assert all(params['profile'] == 'family' for _, params in calls)
    assert calls[-1][1]['session_key'] == 'stored-session'
    with pytest.raises(ValueError):
        AsyncWorktreeHandoffs(Transport(), profile='all')
