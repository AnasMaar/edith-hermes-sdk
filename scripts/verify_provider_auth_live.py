"""Opt-in native Docker auth discovery. Never starts real issuer login.

Creates two isolated profiles and queries provider/account metadata through the
SDK/control plane/native dashboard, then removes only its owned workload.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import tempfile
from pathlib import Path

from edith_hermes import Agent, Docker, Hermes


async def main(image: str) -> None:
    selected = Docker(image=image)
    with tempfile.TemporaryDirectory(prefix="edith-auth-live-") as state:
        async with Hermes.local(runtime=selected, state=str(Path(state) / "state.db")) as hermes:
            instance = await hermes.create_instance(
                "sdk-auth-verification", agents=[Agent("Adam"), Agent("Anas")]
            )
            try:
                for name in ("Adam", "Anas"):
                    profile = instance.agent(name)
                    catalog = await profile.providers.list()
                    codex = await profile.providers("openai-codex").status()
                    accounts = await profile.providers("openai-codex").accounts.list()
                    assert codex["loginSupported"]
                    assert not codex["status"]["loggedIn"]
                    assert accounts["items"] == []
                    assert "token_preview" not in json.dumps([catalog, codex, accounts])
                    print(
                        json.dumps(
                            {
                                "runtime": "docker",
                                "profile": name,
                                "status": "passed",
                                "provider_count": len(catalog["items"]),
                                "codex_login_supported": codex["loginSupported"],
                                "credential_state": codex["status"]["state"],
                            }
                        ),
                        flush=True,
                    )
            finally:
                await instance.delete()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="nousresearch/hermes-agent:latest")
    args = parser.parse_args()
    asyncio.run(main(args.image))
