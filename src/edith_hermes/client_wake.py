"""Wake detection on an owned duplex connection with client microphone bytes.

This deliberately refuses execution-host capture. One persistent connection
owns start/feed/pause/resume/stop and native wake.detected notifications.
"""
from __future__ import annotations

import base64
from typing import Any

from .duplex import NativeConnection


class AsyncClientWake:
    def __init__(self, connection: NativeConnection):
        self.connection = connection

    async def status(self) -> dict[str, Any]:
        return dict(await self.connection.call("wake.status", surface="gui", client_capture=True, timeout=10))

    async def start(self, *, persist: bool = False) -> dict[str, Any]:
        status = await self.status()
        if status.get("capture") != "client":
            raise ValueError("Configure native wake_word.capture as client before arming this device")
        result = dict(await self.connection.call("wake.start", surface="gui", client_capture=True, persist=persist, timeout=15))
        if result.get("started") is True and result.get("capture") != "client":
            await self.stop()
            raise ValueError("Hermes did not confirm client-device wake capture")
        return result

    async def feed(self, pcm: bytes) -> dict[str, Any]:
        if not pcm or len(pcm) > 64000 or len(pcm) % 2:
            raise ValueError("Choose 1 to 64000 bytes of mono 16 kHz int16 PCM")
        return dict(await self.connection.call("wake.feed", pcm_b64=base64.b64encode(pcm).decode("ascii"), sample_rate=16000, timeout=10))

    async def pause(self) -> dict[str, Any]:
        return dict(await self.connection.call("wake.pause", timeout=10))

    async def resume(self) -> dict[str, Any]:
        return dict(await self.connection.call("wake.resume", timeout=10))

    async def stop(self, *, persist: bool = False) -> dict[str, Any]:
        return dict(await self.connection.call("wake.stop", persist=persist, timeout=10))
