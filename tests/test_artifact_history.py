import httpx
import pytest

from edith_hermes.artifact_history import AsyncArtifactHistory
from edith_hermes.command_center import AsyncCommandCenter
from edith_hermes.desktop import AsyncHermesDesktop
from edith_hermes.kanban import AsyncKanban


@pytest.mark.asyncio
async def test_native_artifact_pagination_keeps_concrete_profile_and_compacted_history():
    requests = []
    def response(request):
        requests.append(request)
        assert request.url.params['profile'] == 'family'
        assert request.headers['authorization'] == 'Bearer secret'
        if request.url.path == '/api/profiles/sessions':
            return httpx.Response(200, json={'sessions': [{'id': 'canonical', 'profile': 'family'}], 'total': 150})
        assert request.url.params['offset'] == '100'
        assert request.url.params['include_compacted'] == 'true'
        assert request.url.params['inline_images'] == 'false'
        return httpx.Response(200, json={'profile': 'family', 'session_id': 'canonical', 'messages': []})
    async with httpx.AsyncClient(base_url='http://native', transport=httpx.MockTransport(response)) as http:
        history = AsyncArtifactHistory(AsyncHermesDesktop(http, 'family', token='secret'))
        await history.sessions(offset=50)
        await history.messages('canonical', offset=100)
    assert len(requests) == 2


@pytest.mark.asyncio
async def test_foreign_profile_history_is_rejected():
    async with httpx.AsyncClient(base_url='http://native', transport=httpx.MockTransport(lambda _: httpx.Response(200, json={'profile': 'door', 'messages': []}))) as http:
        with pytest.raises(ValueError, match='another profile'):
            await AsyncArtifactHistory(AsyncHermesDesktop(http, 'family')).messages('same-id')


@pytest.mark.asyncio
async def test_command_center_and_kanban_use_native_routes_without_flipping_current_board():
    requests = []
    def response(request):
        requests.append(request)
        assert request.url.params['profile'] == 'family'
        if request.url.path.startswith('/api/plugins/kanban/'):
            assert request.url.params['board'] == 'work-board'
        return httpx.Response(200, json={})
    async with httpx.AsyncClient(base_url='http://native', transport=httpx.MockTransport(response)) as http:
        desktop = AsyncHermesDesktop(http, 'family')
        center = AsyncCommandCenter(desktop)
        await center.status()
        await center.usage(days=7)
        await center.logs(search='warning')
        await AsyncKanban(desktop, board='work-board').snapshot()
        await AsyncKanban(desktop, board='work-board').orchestration()
    assert [request.url.path for request in requests] == ['/api/status', '/api/analytics/usage', '/api/logs', '/api/plugins/kanban/board', '/api/plugins/kanban/orchestration']


@pytest.mark.asyncio
async def test_artifact_content_is_bound_to_its_originating_session_and_profile():
    def response(request):
        assert request.url.path == '/api/fs/read-data-url'
        assert dict(request.url.params) == {'session_id': 'canonical', 'path': './été.png', 'profile': 'family'}
        assert request.headers['authorization'] == 'Bearer backend-only'
        return httpx.Response(200, json={'dataUrl': 'data:image/png;base64,YQ=='})
    async with httpx.AsyncClient(base_url='http://native', transport=httpx.MockTransport(response)) as http:
        desktop = AsyncHermesDesktop(http, 'family', token='backend-only')
        assert await AsyncArtifactHistory(desktop).file('canonical', './été.png') == {'dataUrl': 'data:image/png;base64,YQ=='}


@pytest.mark.asyncio
async def test_originating_session_detail_keeps_owner_and_native_managed_source():
    def response(request):
        assert request.url.path == '/api/sessions/native%2Fsession' or request.url.path == '/api/sessions/native/session'
        assert request.url.params['profile'] == 'family'
        return httpx.Response(200, json={'id': 'native/session', 'profile': 'family', 'source': 'cron', 'scheduler_owned': True})
    async with httpx.AsyncClient(base_url='http://native', transport=httpx.MockTransport(response)) as http:
        row = await AsyncArtifactHistory(AsyncHermesDesktop(http, 'family')).session('native/session')
        assert row['scheduler_owned'] is True
