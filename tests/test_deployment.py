import httpx
import pytest

from edith_hermes.deployment import AsyncDeployment
from edith_hermes.desktop import AsyncHermesDesktop


@pytest.mark.asyncio
async def test_native_install_identity_preserves_profile_scope_and_credentials():
    def response(request):
        assert request.url.path == '/api/status'
        assert request.url.params['profile'] == 'family'
        assert request.headers['authorization'] == 'Bearer private-token'
        return httpx.Response(200, json={'install_id': 'a' * 32, 'pid': 999, 'version': 'ignored'})
    async with httpx.AsyncClient(base_url='http://hermes', transport=httpx.MockTransport(response)) as http:
        client = AsyncHermesDesktop(http, 'family', token='private-token')
        assert await AsyncDeployment(client).identity() == {'installId': 'a' * 32}


@pytest.mark.asyncio
@pytest.mark.parametrize('identity', [None, 'ephemeral-process-123'])
async def test_missing_identity_is_unsupported_instead_of_a_fabricated_id(identity):
    async with httpx.AsyncClient(base_url='http://hermes', transport=httpx.MockTransport(lambda request: httpx.Response(200, json={'install_id': identity}))) as http:
        with pytest.raises(ValueError, match='persistent Hermes installation identity'):
            await AsyncDeployment(AsyncHermesDesktop(http, 'family')).identity()
