import pytest

from edith_hermes.kanban_management import AsyncKanbanManagement


@pytest.mark.asyncio
async def test_management_owns_concrete_profile_board_revision_and_nonce_without_replay():
    calls = []

    class RPC:
        async def call(self, method, **params):
            calls.append((method, params))
            return {'status': 'applied', 'requestId': params.get('request_id')}

    sdk = AsyncKanbanManagement(RPC(), profile='door')
    await sdk.task_action('home-board', 'task-one', 'task-revision', action='link', request_id='link-once', payload={'childId': 'task-two'})
    await sdk.board_action('home-board', action='archive', request_id='archive-once', revision='board-revision', payload={})
    await sdk.change_orchestration('configuration-revision', request_id='config-once', changes={'auto_decompose': False})
    await sdk.operation('archive-once')
    assert all(params['profile'] == 'door' for _, params in calls)
    assert calls[0][1]['board'] == 'home-board' and calls[0][1]['revision'] == 'task-revision'
    assert calls[1][1]['request_id'] == 'archive-once'
    assert calls[2][1]['changes'] == {'auto_decompose': False}
    assert calls[3][0].endswith('.operation')


@pytest.mark.asyncio
async def test_unsupported_or_lost_native_management_response_is_not_retried():
    calls = []

    class RPC:
        async def call(self, method, **params):
            calls.append(method)
            raise TimeoutError('Unknown native mutation outcome')

    with pytest.raises(TimeoutError):
        await AsyncKanbanManagement(RPC(), profile='default').board_action('board', action='create', request_id='one', revision=None, payload={'name': 'Native board'})
    assert len(calls) == 1
    with pytest.raises(ValueError):
        AsyncKanbanManagement(RPC(), profile='all')


@pytest.mark.asyncio
async def test_native_worker_operations_use_checked_management_boundary():
    calls = []

    class RPC:
        async def call(self, method, **params):
            calls.append((method, params))
            return {}

    sdk = AsyncKanbanManagement(RPC(), profile='door')
    await sdk.workers('board')
    await sdk.board_action('board', action='dispatch', request_id='dispatch-once', revision='board-revision', payload={'dryRun': True, 'max': 2})
    await sdk.task_action('board', 'task', 'task-revision', action='decompose', request_id='decompose-once', payload={})
    await sdk.task_action('board', 'task', 'task-revision', action='delete', request_id='delete-once', payload={'confirmed': True})
    assert calls[0] == ('edith.desktop.v1.kanban.management.workers', {'profile': 'door', 'board': 'board'})
    assert [params.get('action') for _, params in calls[1:]] == ['dispatch', 'decompose', 'delete']
