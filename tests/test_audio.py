import httpx
import pytest

from edith_hermes.audio import AsyncHermesAudio
from edith_hermes.desktop import AsyncHermesDesktop


@pytest.mark.asyncio
async def test_audio_uses_profile_scoped_client_bytes_and_never_backend_devices_or_provider_keys():
    calls = []

    def handler(request):
        calls.append(request)
        if request.url.path.endswith("transcribe"):
            return httpx.Response(
                200, json={"ok": True, "transcript": "Scoped speech", "provider": "native"}
            )
        if request.url.path.endswith("speak"):
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "data_url": "data:audio/wav;base64,YQ==",
                    "mime_type": "audio/wav",
                    "provider": "native",
                },
            )
        return httpx.Response(200, json={"available": False, "reason": "No realtime provider"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://native.invalid"
    ) as http:
        service = AsyncHermesAudio(AsyncHermesDesktop(http, "door", token="backend-only"))
        assert (await service.transcribe("data:audio/webm;base64,YQ==", mime_type="audio/webm"))[
            "transcript"
        ] == "Scoped speech"
        assert (await service.speak("Read this"))["data_url"].startswith("data:audio/")
        assert (await service.live_status())["available"] is False
        assert all(request.url.params["profile"] == "door" for request in calls)
        assert [request.url.path for request in calls] == [
            "/api/audio/transcribe",
            "/api/audio/speak",
            "/api/audio/voice-live/status",
        ]
        with pytest.raises(ValueError):
            await service.transcribe("file:///remote-mic.wav", mime_type="audio/wav")
        with pytest.raises(ValueError):
            await service.speak("")
