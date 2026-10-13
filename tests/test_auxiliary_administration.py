import pytest

from edith_hermes.auxiliary_administration import AsyncAuxiliaryAdministration


@pytest.mark.asyncio
async def test_task_defaults_are_scoped_checked_and_mutations_are_never_retried():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith(".list"):
                return {"tasks": []}
            raise TimeoutError("Accepted save lost reply")

    api = AsyncAuxiliaryAdministration(Transport(), profile="door")
    assert await api.tasks() == []
    with pytest.raises(TimeoutError):
        await api.change(
            "summary", revision="current", request_id="one", provider="auto", model="", effort=None
        )
    assert len(calls) == 2 and calls[-1][1] == dict(
        profile="door",
        task="summary",
        revision="current",
        request_id="one",
        provider="auto",
        model="",
        effort=None,
        confirmed=False,
        timeout=180,
    )
    with pytest.raises(ValueError):
        AsyncAuxiliaryAdministration(Transport(), profile="all")
