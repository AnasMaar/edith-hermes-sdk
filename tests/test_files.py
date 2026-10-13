import pytest

from edith_hermes.files import AsyncFiles


class RPC:
    def __init__(self):
        self.calls = []

    async def call(self, method, **params):
        self.calls.append((method, params))
        return {'status': 'applied'}


@pytest.mark.asyncio
async def test_file_requests_keep_native_paths_profile_revision_and_single_mutation():
    rpc = RPC()
    files = AsyncFiles(rpc, profile='family')
    await files.read('C:/remote/été.txt', include_data=False)
    await files.save('C:/remote/été.txt', workspace_root='C:/remote', revision='stale-check', content='New content', request_id='one')
    await files.operation('one')
    assert rpc.calls[0] == ('edith.desktop.v1.files.read', {'profile': 'family', 'path': 'C:/remote/été.txt', 'include_data': False})
    assert rpc.calls[1][1]['revision'] == 'stale-check'
    assert rpc.calls[1][1]['request_id'] == rpc.calls[2][1]['request_id'] == 'one'
    assert len(rpc.calls) == 3


def test_file_profile_cannot_fall_back_to_all():
    with pytest.raises(ValueError, match='concrete owning profile'):
        AsyncFiles(RPC(), profile='all')
