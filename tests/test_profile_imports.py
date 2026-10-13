import pytest

from edith_hermes.profile_imports import AsyncProfileImports


@pytest.mark.asyncio
async def test_reviewed_import_retains_source_scope_target_and_durable_request():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('.start'):
                raise TimeoutError('Native new profile may already exist')
            return dict(profileId='family', imports=[], externalUploadSupported=False)

    service = AsyncProfileImports(Transport(), profile='family')
    assert (await service.inventory())['externalUploadSupported'] is False
    await service.review('owned-export')
    with pytest.raises(TimeoutError):
        await service.start(request_id='once', export_id='owned-export', revision='checked', name='new-profile')
    assert calls[-1][1] == dict(profile='family', request_id='once', export_id='owned-export', revision='checked', name='new-profile', timeout=180)
    await service.operation('once')
    assert calls[-1][1] == dict(profile='family', request_id='once')
    with pytest.raises(ValueError):
        AsyncProfileImports(Transport(), profile='all')
