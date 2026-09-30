"""Login to a model provider on an existing SDK instance/profile.

This explicitly starts user consent. It does not provision/delete instances,
copy local account credentials or run paid inference. Set EDITH_CONTROL_PLANE_TOKEN
only if your control plane requires authentication.

uv run python examples/provider_login.py --url http://localhost:8080 \
    --instance INSTANCE_ID --profile PROFILE_ID --provider openai-codex --open-browser
"""

from __future__ import annotations

import argparse
import asyncio
import os

from edith_hermes import Hermes, ProviderLoginError


async def main(args: argparse.Namespace) -> None:
    async with Hermes.remote(
        base_url=args.url, token=os.getenv("EDITH_CONTROL_PLANE_TOKEN")
    ) as hermes:
        profile = hermes.instances(args.instance).profiles(args.profile)
        provider = profile.providers(args.provider)
        status = await provider.status()
        if not status["loginSupported"]:
            print("External login required:", status.get("cliCommand"), status.get("docsUrl"))
            return
        login = await provider.login(open_browser=args.open_browser)
        print("Login:", login.id)
        print("Open:", login.verification_url)
        print("Code:", login.user_code, flush=True)
        try:
            await login.wait(timeout=args.timeout)
        except ProviderLoginError as exc:
            print("Login ended:", exc.login["status"], exc.login["errorCode"])
            raise
        except TimeoutError:
            print(
                "Waiting timed out. Native login is still active; reattach by ID or cancel explicitly."
            )
            raise
        print("Approved for the selected instance/profile. Credentials stay in Hermes.")
        if args.model:
            await profile.update(provider=args.provider, model=args.model)
            print("Profile now uses:", args.provider, args.model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--provider", default="openai-codex")
    parser.add_argument(
        "--model", help="Optionally select this model after approval; no inference is run"
    )
    parser.add_argument("--open-browser", action="store_true")
    parser.add_argument("--timeout", type=float, default=900)
    asyncio.run(main(parser.parse_args()))
