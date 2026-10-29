"""Read control-plane instances and sessions without creating anything."""

import argparse
import asyncio
import json
import os

from edith_hermes import AsyncEdithHermes


async def inspect(sdk, instance_id, profile_id):
    instances = await sdk.control_plane.list_instances()
    sessions = await sdk.runtime.list_sessions(instance_id=instance_id, profile_id=profile_id)
    return {"instances": instances, "sessions": sessions}


async def main(args):
    async with AsyncEdithHermes.remote(base_url=args.url, token=os.getenv("EDITH_TOKEN")) as sdk:
        print(json.dumps(await inspect(sdk, args.instance, args.profile), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Control-plane HTTP URL")
    parser.add_argument("--instance", required=True)
    parser.add_argument("--profile", required=True)
    asyncio.run(main(parser.parse_args()))
