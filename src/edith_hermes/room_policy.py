"""Canonical bot policy through exact native RoomLink approval frames."""
from typing import Any, cast

from .extensions import ExtensionTransport


class AsyncRoomPolicy:
    def __init__(self, connection: ExtensionTransport, *, profile: str):
        self.connection, self.profile = connection, profile

    async def authorize(
        self, *, room_id: str, member_id: str, target_install_id: str,
        target_profile: str, catalog_digest: str
    ) -> dict[str, Any]:
        return cast(dict[str, Any], await self.connection.call(
            'edith.desktop.v1.groups.peer.authorize', profile=self.profile,
            room_id=room_id, member_id=member_id, target_install_id=target_install_id,
            target_profile=target_profile, catalog_digest=catalog_digest))
