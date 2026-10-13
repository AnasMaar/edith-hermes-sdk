"""Byte-exact client WebRTC negotiation through Hermes's native Desktop API.

Provider credentials stay on Hermes. The peer connection, microphone, speaker,
delegation data channel and session close belong to the calling client.
"""
from __future__ import annotations

from typing import Literal, TypedDict, cast

from .desktop import AsyncHermesDesktop


class LiveAudioStatus(TypedDict):
    ok: bool
    mode: Literal["chained", "gpt-live"]
    available: bool
    reason: str | None
    model: str
    voice: str


class LiveAudioSession(TypedDict):
    id: str


class LiveAudioTransport(TypedDict):
    type: Literal["webrtc"]
    sdp: str


class LiveAudioAnswer(TypedDict):
    ok: bool
    session: LiveAudioSession
    transport: LiveAudioTransport


class AsyncLiveAudio:
    def __init__(self, desktop: AsyncHermesDesktop):
        self.desktop = desktop

    async def status(self) -> LiveAudioStatus:
        result = await self.desktop._request("GET", "/api/audio/voice-live/status")
        if not isinstance(result, dict) or result.get("ok") is not True or result.get("mode") not in {"chained", "gpt-live"} or not isinstance(result.get("available"), bool):
            raise ValueError("Hermes returned an invalid live audio status")
        # Only documented non-secret readiness fields are returned.
        return cast(LiveAudioStatus, {key: result.get(key) for key in ("ok", "mode", "available", "reason", "model", "voice")})

    async def negotiate(self, sdp: str) -> LiveAudioAnswer:
        if not sdp.strip() or len(sdp.encode("utf-8")) > 256 * 1024:
            raise ValueError("Choose a nonempty client SDP offer up to 256 KiB")
        # Do not strip: the native vendor SDP parser requires the trailing CRLF.
        # Never retry a mutation whose response could have been lost.
        result = await self.desktop._request("POST", "/api/audio/voice-live/session", body={"sdp": sdp}, timeout=45)
        if not isinstance(result, dict) or result.get("ok") is not True:
            raise ValueError("Hermes rejected live audio negotiation")
        session, transport = result.get("session"), result.get("transport")
        if not isinstance(session, dict) or not isinstance(session.get("id"), str) or not session["id"] or not isinstance(transport, dict) or transport.get("type") != "webrtc" or not isinstance(transport.get("sdp"), str) or not transport["sdp"].strip() or len(transport["sdp"].encode("utf-8")) > 256 * 1024:
            raise ValueError("Hermes returned an invalid WebRTC answer")
        return cast(LiveAudioAnswer, {"ok": True, "session": {"id": session["id"]}, "transport": {"type": "webrtc", "sdp": transport["sdp"]}})
