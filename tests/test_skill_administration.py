import pytest

from edith_hermes.skill_administration import AsyncSkillAdministration


@pytest.mark.asyncio
async def test_checked_action_has_canonical_scope_revision_and_no_retry():
    calls=[]
    class Transport:
        async def call(self,method,**params):
            calls.append((method,params))
            raise TimeoutError('Accepted action may have lost its reply')
    admin=AsyncSkillAdministration(Transport(),profile='family')
    with pytest.raises(TimeoutError):
        await admin.change('skill-owned',revision='r1',kind='update',request_id='once')
    assert calls==[('edith.desktop.v1.skills.checkedAction',dict(profile='family',id='skill-owned',revision='r1',kind='update',request_id='once',timeout=180))]
    with pytest.raises(ValueError):
        AsyncSkillAdministration(Transport(),profile='all')
