import pytest

from edith_hermes.profile_archives import AsyncProfileArchives


@pytest.mark.asyncio
async def test_upload_keeps_concrete_owner_identity_offset_and_native_review():
    class Transport:
        def __init__(self):
            self.calls = []

        async def call(self, method, **params):
            self.calls.append((method, params))
            return {'id': 'once', 'receivedBytes': 3}

    transport = Transport()
    client = AsyncProfileArchives(transport, profile='door')
    await client.begin(request_id='once', filename='Profile é.zip', size_bytes=3, revision='a' * 64)
    await client.append('once', offset=0, data_base64='YWJj')
    await client.status('once')
    await client.complete('once')
    assert all(params['profile'] == 'door' and params['request_id'] == 'once' for _, params in transport.calls)
    assert transport.calls[1][1]['offset'] == 0
    with pytest.raises(ValueError):
        AsyncProfileArchives(transport, profile='all')
