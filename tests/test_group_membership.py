import pytest

from edith_hermes.group_membership import AsyncGroupMembership


@pytest.mark.asyncio
async def test_idle_retirement_owns_the_exact_native_room_revision():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return {'roomId': params['room_id'], 'retired': True}

    result = await AsyncGroupMembership(Connection()).retire_idle('native-room', latest_seq=17)
    assert result == {'roomId': 'native-room', 'retired': True}
    assert calls == [('edith.desktop.v1.groups.retire-idle', {'room_id': 'native-room', 'latest_seq': 17})]
