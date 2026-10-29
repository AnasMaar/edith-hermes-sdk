"""Create a native session, submit a prompt and display events on the same connection."""

import argparse
import asyncio
import json
import os

from edith_hermes import Hermes


async def run(connection, prompt, limit, timeout):
    session = await connection.call(
        "session.create", title="SDK example", close_on_disconnect=False
    )
    session_id = session["session_id"]
    print("session:", json.dumps(session), flush=True)
    before = await connection.call("session.events.since", session_id=session_id, last_seen=0)
    cursor, epoch = before["latest_seq"], before["epoch"]
    await connection.call("prompt.submit", session_id=session_id, text=prompt)
    events = connection.events()
    for _ in range(limit):
        try:
            frame = await asyncio.wait_for(anext(events), timeout=timeout)
        except (asyncio.TimeoutError, ConnectionError, StopAsyncIteration):
            print(
                "Event stream idle or disconnected; turn status is uncertain. Inspect session",
                session_id,
            )
            return
        print(json.dumps(frame))
        # Server requests are displayed but never answered automatically.
        try:
            replay = await connection.call(
                "session.events.since", session_id=session_id, last_seen=cursor
            )
        except (ConnectionError, TimeoutError):
            print("Replay unavailable; turn status is uncertain. Inspect session", session_id)
            return
        if replay["truncated"] or replay["epoch"] != epoch:
            print(
                "Event replay changed or was truncated; turn status is uncertain. Inspect session",
                session_id,
            )
            return
        cursor = replay["latest_seq"]
        for event in replay["events"]:
            if event.get("type") == "message.complete":
                payload = event.get("payload") or {}
                status = (
                    "failed"
                    if payload.get("error") or payload.get("status") == "error"
                    else ("stopped" if payload.get("status") == "interrupted" else "completed")
                )
                print("turn status:", status)
                return
    print("Event limit reached; turn status is uncertain. Inspect session", session_id)


async def main(args):
    if not args.run:
        raise SystemExit("Pass --run to create a session and submit a potentially billable prompt")
    async with (
        Hermes.remote(args.url, token=os.getenv("EDITH_TOKEN")) as hermes,
        hermes.instances(args.instance).profiles(args.profile).connect() as connection,
    ):
        await run(connection, args.prompt, args.limit, args.timeout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--limit", type=int, default=10, help="Maximum event frames")
    parser.add_argument("--timeout", type=float, default=30, help="Seconds to wait per frame")
    asyncio.run(main(parser.parse_args()))
