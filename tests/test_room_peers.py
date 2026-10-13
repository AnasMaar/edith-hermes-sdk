import pytest

from edith_hermes.room_peers import AsyncRoomPeers


@pytest.mark.asyncio
async def test_room_peers_preserve_exact_profile_and_native_scope():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return {}

    sdk = AsyncRoomPeers(Connection(), profile='door')
    invitation = dict(room_id='home-room', home_install_id='home', authority_gateway_id='home',
                      authority_epoch=1, member_id='member', grant_id='exact', ttl_seconds=3600)
    await sdk.capabilities()
    await sdk.invite(request_id='once', capability_digest='a'*64, invitation=invitation)
    await sdk.operation('once')
    await sdk.route(room_id='home-room', member_id='member')
    await sdk.register(room_id='home-room', member_id='member', target_url='https://peer',
                       target_profile='family', grant='private', cancellation_scope_id='cancel', trace_id='trace')
    await sdk.revoke('private')
    assert [method for method, _ in calls] == ['groups.capabilities',
        'edith.desktop.v1.groups.peer.invite', 'edith.desktop.v1.groups.peer.operation',
        'edith.desktop.v1.groups.peer.route', 'groups.peer.register', 'groups.peer.revoke']
    assert all(params['profile']=='door' for _, params in calls)
    assert calls[1][1]['invitation'] == invitation
    assert calls[-2][1]['target_profile'] == 'family'
