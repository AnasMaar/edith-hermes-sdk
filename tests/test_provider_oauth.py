import pytest

from edith_hermes.provider_oauth import AsyncProviderOAuth


@pytest.mark.asyncio
async def test_native_login_receipts_have_profile_and_do_not_retry_a_start():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith(".flow"):
                return {"id": params["request_id"], "status": "pending"}
            raise TimeoutError("Native worker may have started")

    api = AsyncProviderOAuth(Transport(), profile="family")
    with pytest.raises(TimeoutError):
        await api.start("nous", request_id="same")
    assert len(calls) == 1 and calls[0][1] == dict(
        profile="family", provider="nous", request_id="same", timeout=180
    )
    assert (await api.flow("same"))["status"] == "pending" and len(calls) == 2
    with pytest.raises(ValueError):
        AsyncProviderOAuth(Transport(), profile="all")
