"""Create a paused schedule and reconcile a timeout using its request ID."""

import argparse
import asyncio
import json
import os
from uuid import uuid4

from edith_hermes import AsyncScheduleMutations, Hermes


async def create(connection, profile_id, request_id, name, prompt, schedule):
    schedules = AsyncScheduleMutations(connection, profile=profile_id)
    options = {"name": name, "prompt": prompt, "schedule": schedule, "paused": True}
    print("request ID:", request_id, flush=True)
    try:
        return await schedules.create(options, request_id=request_id)
    except TimeoutError:
        # A timeout does not establish whether the write happened. Query the same
        # request receipt instead of issuing a second creation.
        return await schedules.operation(request_id)


async def main(args):
    if not args.run:
        raise SystemExit("Pass --run to create a paused schedule")
    async with Hermes.remote(args.url, token=os.getenv("EDITH_TOKEN")) as hermes:
        profile = hermes.instances(args.instance).profiles(args.profile)
        native_profile = (await profile.get())["name"]
        async with profile.connect() as connection:
            result = await create(
                connection, native_profile, str(uuid4()), args.name, args.prompt, args.schedule
            )
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--schedule", required=True, help='For example: "every 2h"')
    parser.add_argument("--run", action="store_true")
    asyncio.run(main(parser.parse_args()))
