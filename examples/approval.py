"""Inspect pending command approvals; optionally respond to one exact request."""

import argparse
import asyncio
import json
import os

from edith_hermes import Hermes


async def inspect_or_respond(profile, session_id, request_id=None, choice=None):
    if request_id is None:
        return await profile.native.approval.pending(session_id=session_id)
    return await profile.native.approval.respond(
        session_id=session_id, request_id=request_id, choice=choice
    )


async def main(args):
    if bool(args.request) != bool(args.choice):
        raise SystemExit("Supply both --request and --choice to respond")
    if args.request and not args.run:
        raise SystemExit("Pass --run to send the approval decision")
    async with Hermes.remote(args.url, token=os.getenv("EDITH_TOKEN")) as hermes:
        profile = hermes.instances(args.instance).profiles(args.profile)
        print(
            json.dumps(
                await inspect_or_respond(profile, args.session, args.request, args.choice), indent=2
            )
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--request")
    parser.add_argument("--choice", choices=["once", "session", "deny"])
    parser.add_argument("--run", action="store_true")
    asyncio.run(main(parser.parse_args()))
