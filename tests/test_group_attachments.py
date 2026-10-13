import pytest

from edith_hermes.group_attachments import AsyncGroupAttachments


@pytest.mark.asyncio
async def test_group_context_routes_canonical_room_attachment_and_event_ids():
    class Connection:
        def __init__(self):
            self.calls = []

        async def call(self, method, **params):
            self.calls.append((method, params))
            return (
                {"events": {"event-a": [{"id": "file-a"}]}}
                if method.endswith(".attachment-metadata")
                else {"id": "file-a"}
            )

    connection = Connection()
    sdk = AsyncGroupAttachments(connection)
    assert (
        await sdk.stage("room-a", attachment_id="file-a", name="file.txt", content_base64="YQ==")
    )["id"] == "file-a"
    await sdk.send(
        "room-a", event_id="request-a", payload={"text": "Read file"}, attachment_ids=["file-a"]
    )
    assert (await sdk.metadata("room-a", event_ids=["event-a"]))["event-a"][0]["id"] == "file-a"
    await sdk.content("room-a", attachment_id="file-a")
    assert connection.calls[0] == (
        "edith.desktop.v1.groups.stage-attachment",
        {
            "room_id": "room-a",
            "attachment_id": "file-a",
            "name": "file.txt",
            "content_base64": "YQ==",
        },
    )
    assert connection.calls[1][1]["event_id"] == "request-a" and connection.calls[1][1][
        "attachment_ids"
    ] == ["file-a"]
