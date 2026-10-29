"""Send one message to the Bot Chat on an explicitly selected sandbox profile."""

import argparse
import asyncio
import json
import os

from edith_hermes import Hermes


async def send(profile, message):
    return await profile.native.bot_relay.deliver(message=message)


async def main(args):
    if not args.run:
        raise SystemExit("Pass --run to deliver a potentially billable bot message")
    async with Hermes.remote(args.url, token=os.getenv("EDITH_TOKEN")) as hermes:
        profile = hermes.instances(args.instance).profiles(args.profile)
        print(json.dumps(await send(profile, args.message), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--run", action="store_true")
    asyncio.run(main(parser.parse_args()))
