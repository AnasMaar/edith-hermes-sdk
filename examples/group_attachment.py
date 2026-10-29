"""Stage and send a local file to an explicitly selected group room."""

import argparse
import asyncio
import base64
import json
import os
from pathlib import Path
from uuid import uuid4

from edith_hermes import AsyncGroupAttachments, Hermes


async def send(connection, room_id, file_path, message):
    attachments = AsyncGroupAttachments(connection)
    attachment_id, event_id = str(uuid4()), str(uuid4())
    staged = await attachments.stage(
        room_id,
        attachment_id=attachment_id,
        name=file_path.name,
        content_base64=base64.b64encode(file_path.read_bytes()).decode(),
    )
    result = await attachments.send(
        room_id, event_id=event_id, payload={"text": message}, attachment_ids=[staged["id"]]
    )
    return {"attachment": staged, "event_id": event_id, "result": result}


async def main(args):
    if not args.run:
        raise SystemExit("Pass --run to stage and send an attachment")
    async with (
        Hermes.remote(args.url, token=os.getenv("EDITH_TOKEN")) as hermes,
        hermes.instances(args.instance).profiles(args.profile).connect() as connection,
    ):
        print(json.dumps(await send(connection, args.room, args.file, args.message), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--room", required=True)
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--message", required=True)
    parser.add_argument("--run", action="store_true")
    asyncio.run(main(parser.parse_args()))
