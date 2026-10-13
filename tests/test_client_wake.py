from typing import cast

import pytest

from edith_hermes.client_wake import AsyncClientWake
from edith_hermes.duplex import NativeConnection


@pytest.mark.asyncio
async def test_owned_client_wake_lifecycle_never_records_on_execution_host():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return {"capture": "client", "available": True, "started": True}

    service = AsyncClientWake(cast(NativeConnection, Connection()))
    await service.start(persist=True)
    await service.feed(b"\x00\x00" * 1280)
    await service.pause()
    await service.resume()
    await service.stop()
    assert [method for method, _ in calls] == ["wake.status", "wake.start", "wake.feed", "wake.pause", "wake.resume", "wake.stop"]
    assert calls[0][1]["client_capture"] is True
    assert calls[1][1]["surface"] == "gui"
    assert calls[2][1]["sample_rate"] == 16000
    with pytest.raises(ValueError):
        await service.feed(b"x")


@pytest.mark.asyncio
async def test_native_auto_capture_that_would_choose_the_execution_host_is_refused():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append(method)
            return {"capture": "local", "available": True}

    with pytest.raises(ValueError, match="client"):
        await AsyncClientWake(cast(NativeConnection, Connection())).start(persist=True)
    assert calls == ["wake.status"]
