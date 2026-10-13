from edith_hermes.git_mutations import AsyncGitMutations


async def test_mutation_and_reconciliation_keep_profile_and_request_identity():
    calls=[]
    class Transport:
        async def call(self, method, **kwargs):
            calls.append((method,kwargs))
            return {'id':'once','profileId':'family','path':'C:/été','action':'commit',
                    'status':'applied','beforeHead':'old','result':{'head':'new'}}
    client=AsyncGitMutations(Transport(),profile='family')
    assert (await client.mutate('C:/été','commit',request_id='once',message='A commit',include_unstaged=False))['status']=='applied'
    await client.operation('once')
    assert calls[0][0]=='edith.desktop.v1.git.mutate'
    assert calls[0][1]['includeUnstaged'] is False
    assert calls[0][1]['profile']=='family' and calls[0][1]['request_id']=='once'
    assert calls[1]==('edith.desktop.v1.git.operation',{'profile':'family','request_id':'once'})
    await client.mutate('C:/été','create-pr',request_id='draft',head_branch='feature',base_branch='main',
                        is_draft=True,title='My title',body='Line one\nLine two')
    assert calls[-1][1]['isDraft'] is True
    assert calls[-1][1]['headBranch']=='feature' and calls[-1][1]['body']=='Line one\nLine two'
    await client.mutate('C:/été','create-branch',request_id='branch',branch='feature',fail_if_exists=True)
    assert calls[-1][1]['failIfExists'] is True
