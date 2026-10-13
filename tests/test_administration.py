import json

import httpx
import pytest

from edith_hermes.administration import DesktopAdministration
from edith_hermes.desktop import AsyncHermesDesktop


@pytest.mark.asyncio
async def test_native_administration_scope_routes_secrets_and_job_receipts():
    requests=[]

    def receive(request):
        requests.append(request)
        assert request.url.params['profile']=='door'
        return httpx.Response(200,json={'ok':True,'job_id':'native-job','session_id':'login'})

    async with httpx.AsyncClient(base_url='http://hermes',transport=httpx.MockTransport(receive)) as http:
        api=DesktopAdministration(AsyncHermesDesktop(http,'door'))
        await api.providers.set_key('PROVIDER_KEY','secret')
        await api.providers.test_key('PROVIDER_KEY','secret')
        await api.providers.remove_key('PROVIDER_KEY')
        endpoint={'name':'Local','base_url':'http://localhost:9090/v1','model':'local'}
        await api.providers.save_endpoint(endpoint)
        await api.providers.test_endpoint(endpoint)
        await api.providers.activate_endpoint('endpoint-été')
        await api.providers.remove_endpoint('endpoint-été')
        await api.providers.start_login('nous')
        await api.providers.login('nous','saved-login')
        await api.providers.cancel_login('saved-login')
        await api.providers.disconnect('nous')
        await api.models.assign({'scope':'auxiliary','provider':'auto','model':'default','task':'summary','reasoning_effort':None})
        receipt=await api.local_models.download('family/model')
        assert receipt['job_id']=='native-job' and 'status' not in receipt
        await api.local_models.pause_download('native-job')
        await api.local_models.resume_download('native-job')
        await api.local_models.activate('variant')
        await api.local_models.server('stop')
        await api.channels.save('discord',{'env':{'TOKEN':'secret'},'clear_env':[]})
        await api.memory.save_node('memory:memory:0:fingerprint','replacement')
        await api.memory.remove_node('memory:profile:1:fingerprint')
        await api.profiles.restore('C:/archive.zip')
    assert json.loads(requests[0].content)=={'key':'PROVIDER_KEY','value':'secret','profile':'door','provider_setup':True}
    assert 'secret' not in str(requests[0].url)
    assignment=json.loads(requests[11].content)
    assert assignment['reasoning_effort'] is None and assignment['task']=='summary'
    assert json.loads(requests[17].content)=={'env':{'TOKEN':'secret'},'clear_env':[],'profile':'door'}
    assert requests[18].method=='PUT' and requests[19].method=='DELETE'
    assert json.loads(requests[-1].content)=={'archive':'C:/archive.zip','force':False}


@pytest.mark.asyncio
async def test_read_only_native_coverage_and_measurement_categories_are_preserved():
    paths=[]

    def receive(request):
        paths.append(request.url.path)
        return httpx.Response(200,json={'input_tokens':5,'cache_read_tokens':3,'reasoning_tokens':2,'actual_cost':None,'estimated_cost':0.03})

    async with httpx.AsyncClient(base_url='http://hermes',transport=httpx.MockTransport(receive)) as http:
        api=DesktopAdministration(AsyncHermesDesktop(http,'family'))
        for operation in (api.providers.keys,api.providers.oauth_catalog,api.providers.endpoints,
                          api.models.auxiliary,api.local_models.status,api.local_models.hardware,
                          api.local_models.catalog,api.local_models.jobs,api.memory.status,
                          api.memory.graph,api.channels.list):
            await operation()
        usage=await api.memory.usage(7)
        assert usage['actual_cost'] is None and usage['estimated_cost']==0.03
        assert usage['cache_read_tokens']==3 and usage['reasoning_tokens']==2
        await api.memory.node('memory:memory:0:fingerprint')
    assert len(paths)==13 and '/api/learning/graph' in paths


@pytest.mark.asyncio
async def test_invalid_memory_identity_and_uncertain_mutations_do_not_dispatch_or_replay():
    calls=[]

    def receive(request):
        calls.append(request)
        raise httpx.ReadTimeout('The provider may have accepted this request')

    async with httpx.AsyncClient(base_url='http://hermes',transport=httpx.MockTransport(receive)) as http:
        api=DesktopAdministration(AsyncHermesDesktop(http,'family'))
        with pytest.raises(ValueError):
            await api.memory.save_node('memory:memory:0','draft')
        with pytest.raises(ValueError):
            await api.memory.remove_node('skill-without-safe-revision')
        with pytest.raises(ValueError):
            await api.memory.usage(1000)
        assert not calls
        with pytest.raises(httpx.ReadTimeout):
            await api.providers.start_login('nous')
        assert len(calls)==1
