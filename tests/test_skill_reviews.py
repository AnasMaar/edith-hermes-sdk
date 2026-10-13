import pytest

from edith_hermes.skill_reviews import AsyncSkillReviews


@pytest.mark.asyncio
async def test_review_install_and_reconciliation_retain_exact_profile_bundle_and_request():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            if method.endswith('.install'):
                raise TimeoutError('The exact reviewed bundle may already be published')
            return dict(id='review', profileId='door', resourceId='github/owner/repo/skill', bundleHash='checked')

    client = AsyncSkillReviews(Transport(), profile='door')
    assert (await client.review('github/owner/repo/skill'))['profileId'] == 'door'
    with pytest.raises(TimeoutError):
        await client.install('github/owner/repo/skill', review_id='review', request_id='once', accepted=True)
    assert calls[-1][1] == dict(profile='door', resource='github/owner/repo/skill', review_id='review', request_id='once', accepted=True, timeout=120)
    await client.operation('once')
    assert calls[-1][1] == dict(profile='door', request_id='once')
    with pytest.raises(ValueError):
        AsyncSkillReviews(Transport(), profile='all')
