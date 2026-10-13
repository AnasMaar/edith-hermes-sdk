"""Client-device audio over Hermes's existing profile-scoped Desktop REST API."""
from __future__ import annotations

from typing import TypedDict, cast

from .desktop import AsyncHermesDesktop


class TranscriptionResult(TypedDict):
    ok: bool
    transcript: str
    provider: str | None


class SpeechResult(TypedDict):
    ok: bool
    data_url: str
    mime_type: str
    provider: str | None


class AsyncHermesAudio:
    def __init__(self, desktop: AsyncHermesDesktop):
        self.desktop = desktop

    async def transcribe(self, data_url: str, *, mime_type: str) -> TranscriptionResult:
        if not data_url.startswith("data:") or ";base64," not in data_url or not mime_type.startswith(("audio/", "video/webm")):
            raise ValueError("Choose a base64 client audio recording")
        result = await self.desktop._request("POST", "/api/audio/transcribe", body={"data_url": data_url, "mime_type": mime_type}, timeout=120)
        if not isinstance(result, dict) or result.get("ok") is not True or not isinstance(result.get("transcript"), str):
            raise ValueError("Hermes returned an invalid transcription")
        return cast(TranscriptionResult, result)

    async def speak(self, text: str) -> SpeechResult:
        if not text.strip() or len(text) > 20000:
            raise ValueError("Speech text must contain 1 to 20000 characters")
        result = await self.desktop._request("POST", "/api/audio/speak", body={"text": text}, timeout=120)
        if not isinstance(result, dict) or result.get("ok") is not True or not isinstance(result.get("data_url"), str) or not result["data_url"].startswith("data:audio/"):
            raise ValueError("Hermes returned an invalid speech recording")
        return cast(SpeechResult, result)

    async def live_status(self) -> dict[str, object]:
        """Provider readiness only; this never returns a permanent provider key."""
        return cast(dict[str, object], await self.desktop._request("GET", "/api/audio/voice-live/status"))
