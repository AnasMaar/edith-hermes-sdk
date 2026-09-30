"""Opt-in PostgreSQL storage checks in a disposable, localhost-only container."""

from __future__ import annotations

import asyncio
import json
import secrets
import subprocess
import uuid
from datetime import datetime, timedelta, timezone

from edith_hermes_control_plane.database import Database


def docker(*args: str) -> str:
    return subprocess.check_output(["docker", *args], text=True, timeout=180).strip()


async def main() -> None:
    name = "edith-postgres-verification-" + uuid.uuid4().hex[:12]
    password = secrets.token_hex(24)
    db = None
    created = False
    try:
        docker(
            "run",
            "-d",
            "--name",
            name,
            "-p",
            "127.0.0.1::5432",
            "--tmpfs",
            "/var/lib/postgresql/data",
            "-e",
            f"POSTGRES_PASSWORD={password}",
            "postgres:16-alpine",
        )
        created = True
        port = docker("port", name, "5432/tcp").rsplit(":", 1)[1]
        db = Database(f"postgresql+asyncpg://postgres:{password}@127.0.0.1:{port}/postgres")
        for attempt in range(60):
            try:
                await db.create_schema()
                break
            except (OSError, ConnectionError):
                if attempt == 59:
                    raise
                await asyncio.sleep(1)
        owner = ("test-tenant", "adam")
        await db.put("instance", "test", owner, {"id": "test", "status": "ready"})
        assert (await db.get("instance", "test", owner))["status"] == "ready"
        assert await db.get("instance", "test", ("test-tenant", "anas")) is None
        await db.enqueue("job", "provision", owner, {})
        claims = await asyncio.gather(*(db.claim_job(f"worker-{i}") for i in range(8)))
        assert sum(claim is not None for claim in claims) == 1
        expires = datetime.now(timezone.utc) + timedelta(minutes=1)
        leases = await asyncio.gather(
            *(db.reserve_lease_slot("test", owner, f"lease-{i}", expires) for i in range(8))
        )
        assert sum(leases) == 1
        winner = f"lease-{leases.index(True)}"
        await db.release_lease_slot("test", owner, "not-the-owner")
        assert not await db.reserve_lease_slot("test", owner, "new", expires)
        await db.release_lease_slot("test", owner, winner)
        assert await db.reserve_lease_slot(
            "test", owner, "expired", datetime.now(timezone.utc) - timedelta(seconds=1)
        )
        renewed = await asyncio.gather(
            *(db.reserve_lease_slot("test", owner, f"renewal-{i}", expires) for i in range(8))
        )
        assert sum(renewed) == 1
        await db.release_lease_slot("test", owner, "expired")
        assert not await db.reserve_lease_slot("test", owner, "not-released", expires)
        login = {"id": "login-test", "instanceId": "test", "profileId": "adam", "status": "pending"}
        await db.save_provider_login("login-test", owner, login)
        terminal = {**login, "status": "cancelled"}
        await db.save_provider_login("login-test", owner, terminal)
        stale_polls = await asyncio.gather(
            *(db.save_provider_login("login-test", owner, login) for _ in range(8))
        )
        assert all(row["status"] == "cancelled" for row in stale_polls)
        await db.close()
        db = Database(f"postgresql+asyncpg://postgres:{password}@127.0.0.1:{port}/postgres")
        assert (await db.get("instance", "test", owner))["status"] == "ready"
        assert await db.delete("instance", "test", owner)
        print(
            json.dumps(
                {
                    "provider": "postgresql",
                    "status": "passed",
                    "owner_isolation": True,
                    "exclusive_job_claim": True,
                    "exclusive_lease_claim_and_safe_expiry": True,
                    "reconnect_persistence": True,
                    "provider_login_terminal_state_protected": True,
                }
            )
        )
    finally:
        if db is not None:
            await db.close()
        if created:
            docker("rm", "-f", "-v", name)


if __name__ == "__main__":
    asyncio.run(main())
