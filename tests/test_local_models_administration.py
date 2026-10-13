import pytest

from edith_hermes.local_models_administration import AsyncLocalModelAdministration


@pytest.mark.asyncio
async def test_native_local_model_commands_have_profile_file_revision_and_one_request():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith(".inventory"):
                return {
                    "status": {},
                    "catalog": {},
                    "hardware": {},
                    "profileRevision": "profile",
                    "defaultModel": "",
                    "jobs": [],
                }
            raise TimeoutError("Native job may have been accepted")

    api = AsyncLocalModelAdministration(Transport(), profile="family")
    assert (await api.inventory())["profileRevision"] == "profile"
    with pytest.raises(TimeoutError):
        await api.change(
            "activate", "variant", request_id="one", revision="file", profile_revision="profile"
        )
    assert len(calls) == 2 and calls[-1][1] == dict(
        profile="family",
        kind="activate",
        resource_id="variant",
        request_id="one",
        revision="file",
        profile_revision="profile",
        timeout=180,
    )
    with pytest.raises(ValueError):
        AsyncLocalModelAdministration(Transport(), profile="all")
