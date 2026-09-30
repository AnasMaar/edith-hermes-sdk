"""Run on stdin in the built control-plane image, as its default non-root user.

docker run --rm -i -e EDITH_RUNTIME_PROVIDERS=external --entrypoint python IMAGE -
Feed this script on stdin. No Docker socket, credentials or model is required.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import httpx
from edith_hermes_control_plane.app import create_app
from edith_hermes_control_plane.config import Settings

from edith_hermes import __version__


async def main() -> None:
    assert os.getuid() == 10000, "Image must run as its configured non-root user"
    settings = Settings.from_env()
    assert settings.database_url.startswith("sqlite+aiosqlite:////var/lib/edith/")
    for location in (settings.local_runtime_root, settings.secret_directory):
        directory = Path(location)
        directory.mkdir(parents=True, exist_ok=True)
        probe = directory / "verification-probe"
        probe.write_text("writable", encoding="utf-8")
        probe.unlink()
    app = create_app(settings, start_worker=False)
    async with app.router.lifespan_context(app), httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        live = await client.get("/health/live")
        ready = await client.get("/health/ready")
        assert live.status_code == 200, live.text
        assert live.json()["version"] == __version__, live.text
        assert ready.status_code == 200, ready.text
    print(json.dumps({"check": "nonroot_image_default_sqlite", "status": "passed"}))


if __name__ == "__main__":
    asyncio.run(main())
