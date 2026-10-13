"""Native RoomLink grants and routes with durable invitation reconciliation."""
from typing import Any, Literal, TypedDict, cast

from typing_extensions import NotRequired

from .extensions import ExtensionTransport


class PeerInvitation(TypedDict):
    room_id: str
    home_install_id: str
    authority_gateway_id: str
    authority_epoch: int
    member_id: str
    grant_id: str
    ttl_seconds: int


class PeerGrant(TypedDict):
    grant: str
    catalog: dict[str, Any]
    endpoint: dict[str, Any]
    target_profile: str


class PeerReceipt(TypedDict):
    requestId: str
    input: str
    status: Literal['applied', 'rejected', 'uncertain', 'pending']
    result: NotRequired[PeerGrant]
    error: NotRequired[dict[str, Any]]


class PeerRoute(TypedDict):
    roomId: str
    memberId: str
    targetUrl: str
    targetProfile: str
    targetInstallId: str
    catalogDigest: str
    grantSha256: str
    status: str


class AsyncRoomPeers:
    def __init__(self, connection: ExtensionTransport, *, profile: str):
        self.connection, self.profile = connection, profile

    async def capabilities(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self.connection.call('groups.capabilities', profile=self.profile))

    async def invite(
        self, *, request_id: str, capability_digest: str, invitation: PeerInvitation
    ) -> PeerReceipt:
        """A lost reply must use operation(), never a new invitation identity."""
        return cast(PeerReceipt, await self.connection.call(
            'edith.desktop.v1.groups.peer.invite', profile=self.profile,
            request_id=request_id, capability_digest=capability_digest,
            invitation=invitation))

    async def operation(self, request_id: str) -> PeerReceipt:
        return cast(PeerReceipt, await self.connection.call(
            'edith.desktop.v1.groups.peer.operation', profile=self.profile, request_id=request_id))

    async def route(self, *, room_id: str, member_id: str) -> PeerRoute:
        return cast(PeerRoute, await self.connection.call(
            'edith.desktop.v1.groups.peer.route', profile=self.profile,
            room_id=room_id, member_id=member_id))

    async def register(
        self, *, room_id: str, member_id: str, target_url: str,
        target_profile: str, grant: str, catalog: dict[str, Any], cancellation_scope_id: str, trace_id: str
    ) -> dict[str, Any]:
        return cast(dict[str, Any], await self.connection.call(
            'groups.peer.register', profile=self.profile, room_id=room_id, member_id=member_id,
            target_url=target_url, target_profile=target_profile, grant=grant, catalog=catalog,
            cancellation_scope_id=cancellation_scope_id, trace_id=trace_id))

    async def revoke(self, grant: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self.connection.call('groups.peer.revoke', profile=self.profile, grant=grant))
