import pytest

from edith_hermes.provider_administration import AsyncProviderAdministration


@pytest.mark.asyncio
async def test_checked_provider_bindings_have_profile_revision_and_no_mutation_retry():
    calls=[]

    class Transport:
        async def call(self,method,**params):
            calls.append((method,params))
            if method.endswith('.keys'):
                return {'keys':[]}
            raise TimeoutError('Accepted mutation may have lost its reply')

    provider=AsyncProviderAdministration(Transport(),profile='family')
    assert await provider.keys()==[]
    with pytest.raises(TimeoutError):
        await provider.save_key('OPENAI_API_KEY',revision='one',value='secret',request_id='once')
    assert len(calls)==2
    assert calls[-1]==('edith.desktop.v1.providers.changeKey',dict(profile='family',id='OPENAI_API_KEY',revision='one',value='secret',request_id='once',timeout=180))
    with pytest.raises(ValueError):
        AsyncProviderAdministration(Transport(),profile='all')
