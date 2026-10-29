"""List schedules on a concrete Hermes Desktop profile."""

import argparse
import asyncio
import json
import os

from edith_hermes import AsyncHermesDesktop


async def inspect(desktop):
    return await desktop.cron.list()


async def main(args):
    async with AsyncHermesDesktop.remote(
        base_url=args.url, profile=args.profile, token=os.getenv("HERMES_DESKTOP_TOKEN")
    ) as desktop:
        print(json.dumps(await inspect(desktop), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Hermes Desktop HTTP URL")
    parser.add_argument("--profile", required=True)
    asyncio.run(main(parser.parse_args()))
