import pytest

from edith_hermes.group_dialogue import AsyncGroupDialogue


@pytest.mark.asyncio
async def test_local_group_dialogue_keeps_native_request_and_execution_fences():
    class Connection:
        def __init__(self): self.calls = []
        async def call(self, method, **params):
            self.calls.append((method, params))
            return {'questions': [{'taskId': 'task', 'generation': 2, 'request': {'id': 'srq-canonical'}}]} if method.endswith('.questions') else {'answered': True}
    connection = Connection()
    dialogue = AsyncGroupDialogue(connection)
    assert (await dialogue.pending('room-id'))[0]['request']['id'] == 'srq-canonical'
    assert await dialogue.answer('room-id', task_id='task', execution_generation=2, request_id='srq-canonical', answers={'qid': 'answer'}) == {'answered': True}
    assert connection.calls == [('edith.desktop.v1.groups.questions', {'room_id': 'room-id'}),
                                ('edith.desktop.v1.groups.answer-question', {'room_id': 'room-id', 'task_id': 'task', 'execution_generation': 2, 'request_id': 'srq-canonical', 'answers': {'qid': 'answer'}})]
