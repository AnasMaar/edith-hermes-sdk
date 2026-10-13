import httpx
import pytest

from edith_hermes.desktop import AsyncHermesDesktop
from edith_hermes.kanban import AsyncCheckedKanban, AsyncKanban


@pytest.mark.asyncio
async def test_checked_operations_preserve_board_nonce_revision_without_replay():
    calls = []

    class RPC:
        async def call(self, method, **params):
            calls.append((method, params))
            return {"status": "applied"}

    client = AsyncCheckedKanban(RPC(), board="family-board", profile="family")
    await client.read("opaque/task")
    await client.change(
        request_id="same-nonce",
        task_id="opaque/task",
        revision="stale-fence",
        patch={"title": "New"},
    )
    await client.operation("same-nonce")
    assert len(calls) == 3 and all(p["board"] == "family-board" for _, p in calls)
    assert calls[1][1]["revision"] == "stale-fence"
    assert calls[1][1]["request_id"] == calls[2][1]["request_id"] == "same-nonce"


@pytest.mark.asyncio
async def test_board_inventory_and_workflow_do_not_change_global_board():
    calls = []

    def respond(request):
        calls.append(request)
        assert request.url.params["board"] == "other-board"
        return httpx.Response(200, json={})

    async with httpx.AsyncClient(
        base_url="http://native", transport=httpx.MockTransport(respond)
    ) as http:
        client = AsyncKanban(AsyncHermesDesktop(http, "family"), board="other-board")
        await client.boards()
        await client.workflow()
    assert [r.url.path for r in calls] == [
        "/api/plugins/kanban/boards",
        "/api/plugins/kanban/workflow",
    ]


def test_explicit_board_scope_is_required():
    for board in ("", " spaced "):
        with pytest.raises(ValueError, match="explicit owning"):
            AsyncCheckedKanban(None, board=board, profile="family")
