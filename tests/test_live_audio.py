import json

import httpx
import pytest

from edith_hermes.desktop import AsyncHermesDesktop
from edith_hermes.live_audio import AsyncLiveAudio


@pytest.mark.asyncio
async def test_live_audio_is_profile_bound_byte_exact_secret_filtered_and_never_retried():
    calls = []

    def handle(request):
        calls.append(request)
        if request.method == "GET":
            return httpx.Response(200, json={"ok": True, "mode": "gpt-live", "available": True, "reason": None, "model": "native", "voice": "native", "api_key": "secret"})
        return httpx.Response(200, json={"ok": True, "session": {"id": "session-1", "token": "secret"}, "transport": {"type": "webrtc", "sdp": "v=0\r\n", "key": "secret"}})

    async with httpx.AsyncClient(base_url="https://native.invalid", transport=httpx.MockTransport(handle)) as http:
        service = AsyncLiveAudio(AsyncHermesDesktop(http, "door", token="server-only"))
        assert "api_key" not in await service.status()
        assert await service.negotiate("v=0\r\n") == {"ok": True, "session": {"id": "session-1"}, "transport": {"type": "webrtc", "sdp": "v=0\r\n"}}
        assert json.loads(calls[-1].content) == {"sdp": "v=0\r\n"}
        assert len(calls) == 2
        assert all(request.url.params["profile"] == "door" for request in calls)
        with pytest.raises(ValueError):
            await service.negotiate(" ")
        assert len(calls) == 2


@pytest.mark.asyncio
async def test_uncertain_negotiation_is_not_retried():
    calls = []

    def handle(request):
        calls.append(request)
        raise httpx.ReadTimeout("Reply lost after acceptance", request=request)

    async with httpx.AsyncClient(base_url="https://native.invalid", transport=httpx.MockTransport(handle)) as http:
        with pytest.raises(httpx.ReadTimeout):
            await AsyncLiveAudio(AsyncHermesDesktop(http, "family")).negotiate("v=0\r\n")
        assert len(calls) == 1
