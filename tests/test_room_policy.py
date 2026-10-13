import pytest

from edith_hermes.room_policy import AsyncRoomPolicy


@pytest.mark.asyncio
async def test_canonical_peer_policy_preserves_native_member_and_deployment():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return {'authorized': True}

    result = await AsyncRoomPolicy(Connection(), profile='family').authorize(
        room_id='room', member_id='member', target_install_id='peer', target_profile='door', catalog_digest='exact')
    assert result == {'authorized':True}
    assert calls == [('edith.desktop.v1.groups.peer.authorize', {
        'profile':'family', 'room_id':'room', 'member_id':'member', 'target_install_id':'peer',
        'target_profile':'door', 'catalog_digest':'exact'})]
