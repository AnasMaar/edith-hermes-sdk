import pytest

from edith_hermes.channels_administration import AsyncChannelAdministration


@pytest.mark.asyncio
async def test_checked_channel_bindings_send_changes_only_and_do_not_retry_credentials():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith(".inventory"):
                return {"channels": []}
            raise TimeoutError("A native credential save may be accepted")

    api = AsyncChannelAdministration(Transport(), profile="family")
    assert await api.channels() == []
    with pytest.raises(TimeoutError):
        await api.configure(
            "telegram",
            revision="one",
            request_id="same",
            changes={"env": {"TELEGRAM_BOT_TOKEN": "secret"}},
        )
    assert len(calls) == 2 and calls[-1][1] == dict(
        profile="family",
        id="telegram",
        revision="one",
        request_id="same",
        changes={"env": {"TELEGRAM_BOT_TOKEN": "secret"}},
        timeout=180,
    )
    with pytest.raises(ValueError):
        AsyncChannelAdministration(Transport(), profile="all")
