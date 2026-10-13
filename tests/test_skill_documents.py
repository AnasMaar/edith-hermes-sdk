import pytest

from edith_hermes.skill_documents import AsyncSkillDocuments


@pytest.mark.asyncio
async def test_supporting_file_contract_keeps_profile_skill_relative_path_and_cas():
    calls = []

    class Transport:
        async def call(self, method, **params):
            calls.append((method, params))
            return dict(entries=[], content='own file', revision='one')

    client = AsyncSkillDocuments(Transport(), profile='door')
    assert await client.list('canonical-skill', path='references') == []
    assert (await client.read('canonical-skill', path='references/Unicode é.md'))['revision'] == 'one'
    await client.write('canonical-skill', path='references/Unicode é.md', revision='one', content='updated')
    assert calls[-1][1] == dict(profile='door', id='canonical-skill', path='references/Unicode é.md', revision='one', content='updated')
    await client.remove('canonical-skill', path='references/Unicode é.md', revision='one', request_id='remove-once')
    assert calls[-1][1] == dict(profile='door', id='canonical-skill', path='references/Unicode é.md', revision='one', request_id='remove-once')
    with pytest.raises(ValueError):
        AsyncSkillDocuments(Transport(), profile='all')
