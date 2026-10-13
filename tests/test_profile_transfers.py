import httpx
import pytest

from edith_hermes.desktop import AsyncHermesDesktop
from edith_hermes.profile_transfers import AsyncProfileTransfers


@pytest.mark.asyncio
async def test_exports_retain_native_receipt_and_download_from_original_profile():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('.export'):
                raise TimeoutError('Native child may be accepted')
            if method.endswith('.archive'):
                return {'archive': 'C:/family/backups/one.zip'}
            if method.endswith('.inventory'):
                return {'exports': []}
            return dict(id='one', profileId='family', kind='export', status='running')

    api = AsyncProfileTransfers(Transport(), profile='family')
    with pytest.raises(TimeoutError):
        await api.export(request_id='one')
    assert len(calls) == 1
    assert (await api.operation('one'))['status'] == 'running'
    assert await api.exports() == []

    def response(request):
        assert request.url.params['profile'] == 'family'
        assert request.url.params['archive'] == 'C:/family/backups/one.zip'
        return httpx.Response(200, content=b'PK-archive', headers={'content-type': 'application/zip'})

    async with httpx.AsyncClient(transport=httpx.MockTransport(response), base_url='https://host.test') as http:
        desktop = AsyncHermesDesktop.remote(base_url='https://host.test', profile='family', http_client=http)
        assert await api.download('one', desktop) == b'PK-archive'
        with pytest.raises(ValueError):
            await api.download('one', desktop.for_profile('door'))
