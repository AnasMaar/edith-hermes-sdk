"""Typed native room context extension; room orchestration remains in Hermes."""

from typing import Any, TypedDict, cast

from .extensions import ExtensionTransport


class GroupAttachment(TypedDict):
    id: str
    name: str
    mimeType: str
    kind: str
    size: int
    digest: str


class AsyncGroupAttachments:
    def __init__(self, connection: ExtensionTransport) -> None:
        self.connection = connection

    async def stage(
        self, room_id: str, *, attachment_id: str, name: str, content_base64: str
    ) -> GroupAttachment:
        return cast(
            GroupAttachment,
            await self.connection.call(
                "edith.desktop.v1.groups.stage-attachment",
                room_id=room_id,
                attachment_id=attachment_id,
                name=name,
                content_base64=content_base64,
            ),
        )

    async def send(
        self, room_id: str, *, event_id: str, payload: dict[str, Any], attachment_ids: list[str]
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self.connection.call(
                "edith.desktop.v1.groups.send-attachments",
                room_id=room_id,
                event_id=event_id,
                payload=payload,
                attachment_ids=attachment_ids,
            ),
        )

    async def metadata(
        self, room_id: str, *, event_ids: list[str]
    ) -> dict[str, list[GroupAttachment]]:
        result = await self.connection.call(
            "edith.desktop.v1.groups.attachment-metadata", room_id=room_id, event_ids=event_ids
        )
        return cast(dict[str, list[GroupAttachment]], result["events"])

    async def content(self, room_id: str, *, attachment_id: str) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self.connection.call(
                "edith.desktop.v1.groups.attachment-content",
                room_id=room_id,
                attachment_id=attachment_id,
            ),
        )
