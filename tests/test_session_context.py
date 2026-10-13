import httpx
import pytest

from edith_hermes.desktop import AsyncHermesDesktop
from edith_hermes.session_context import AsyncSessionContexts


@pytest.mark.asyncio
async def test_session_context_inventory_is_bounded_and_rejects_another_profile():
    calls = []
    state = {"profile": "door", "corrupt": False}

    def handler(request):
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "sessions": [
                    {"id": "duplicate-id", "title": "Same title", "profile": state["profile"]}
                ],
                "storage": {"door": "corrupt"} if state["corrupt"] else {},
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://native.invalid"
    ) as http:
        service = AsyncSessionContexts(AsyncHermesDesktop(http, "door", token="backend-secret"))
        assert (await service.list(limit=30))[0]["profile"] == "door"
        assert calls[0].url.params["profile"] == "door" and calls[0].url.params["limit"] == "30"
        assert calls[0].url.params["order"] == "recent" and calls[0].url.params["full"] == "false"
        assert calls[0].headers["Authorization"] == "Bearer backend-secret"
        state["profile"] = "family"
        with pytest.raises(ValueError, match="another profile"):
            await service.list()
        state["profile"] = "door"
        state["corrupt"] = True
        with pytest.raises(ValueError, match="unavailable"):
            await service.list()
        with pytest.raises(ValueError, match="between"):
            await service.list(limit=101)
