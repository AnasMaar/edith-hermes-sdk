from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from edith_hermes_control_plane.database import Database
from edith_hermes_control_plane.providers.docker import DockerProvider


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2Gi", 2147483648),
        ("512Mi", 536870912),
        ("2g", 2147483648),
        ("2G", 2000000000),
        (1024, 1024),
    ],
)
def test_docker_memory_quantities(value, expected):
    assert DockerProvider._memory(value) == expected


@pytest.mark.asyncio
async def test_sqlite_claim_is_exclusive(tmp_path):
    db = Database(f"sqlite+aiosqlite:///{tmp_path / 'claims.db'}")
    await db.create_schema()
    try:
        await db.enqueue("one", "provision", ("local", "owner"), {})
        claims = await asyncio.gather(*(db.claim_job(f"worker-{i}") for i in range(8)))
        assert sum(c is not None for c in claims) == 1
    finally:
        await db.close()


async def test_sqlite_lease_slots_are_exclusive_and_expire_safely(tmp_path):
    db = Database(f"sqlite+aiosqlite:///{tmp_path / 'leases.db'}")
    await db.create_schema()
    owner = ("tenant", "adam")
    expires = datetime.now(timezone.utc) + timedelta(minutes=1)
    try:
        claims = await asyncio.gather(
            *(db.reserve_lease_slot("instance", owner, f"lease-{i}", expires) for i in range(8))
        )
        assert sum(claims) == 1
        winner = f"lease-{claims.index(True)}"
        await db.release_lease_slot("instance", owner, "not-the-winner")
        assert not await db.reserve_lease_slot("instance", owner, "other", expires)
        await db.release_lease_slot("instance", owner, winner)
        assert await db.reserve_lease_slot(
            "instance", owner, "expired", datetime.now(timezone.utc) - timedelta(seconds=1)
        )
        replacements = await asyncio.gather(
            *(
                db.reserve_lease_slot("instance", owner, f"replacement-{i}", expires)
                for i in range(8)
            )
        )
        assert sum(replacements) == 1
        await db.release_lease_slot("instance", owner, "expired")
        assert not await db.reserve_lease_slot("instance", owner, "wrong", expires)
        assert await db.reserve_lease_slot("instance", ("tenant", "anas"), "isolated", expires)
    finally:
        await db.close()
