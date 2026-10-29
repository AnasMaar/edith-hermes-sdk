"""Read native sessions, background agents, groups, plugins and connectors."""

import argparse
import asyncio
import json
import os

from edith_hermes import AsyncHermesConnectors, AsyncPluginCatalog, Hermes


async def inspect(profile, connection, profile_id, plugin):
    return {
        "sessions": await profile.native.session.list(),
        "agents": await profile.native.agents.list(),
        "groups": await profile.native.groups.list(),
        "plugin_catalog": await AsyncPluginCatalog(connection, profile=profile_id).lookup(plugin),
        "connectors": await AsyncHermesConnectors(connection, profile=profile_id).list(),
    }


async def main(args):
    async with Hermes.remote(args.url, token=os.getenv("EDITH_TOKEN")) as hermes:
        profile = hermes.instances(args.instance).profiles(args.profile)
        native_profile = (await profile.get())["name"]
        async with profile.connect() as connection:
            print(
                json.dumps(await inspect(profile, connection, native_profile, args.plugin), indent=2)
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Control-plane HTTP URL")
    parser.add_argument("--instance", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--plugin", required=True, help="Plugin catalog name to look up")
    asyncio.run(main(parser.parse_args()))
