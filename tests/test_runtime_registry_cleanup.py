from __future__ import annotations

import pytest
from edith_hermes_control_plane.database import Database


@pytest.mark.parametrize("target", ["instance", "profile", "session"])
async def test_runtime_deletion_cascades_only_its_owned_descendants(tmp_path, target):
    db = Database(f"sqlite+aiosqlite:///{tmp_path / 'tree.db'}")
    await db.create_schema()
    owner = ("tenant", "adam")
    other_owner = ("tenant", "anas")
    documents = [
        ("instance", "i", {"id": "i"}),
        ("instance", "other", {"id": "other"}),
        ("profile", "p", {"id": "p", "instanceId": "i"}),
        ("profile", "other-profile", {"id": "other-profile", "instanceId": "i"}),
        ("session", "s", {"id": "s", "instanceId": "i", "profileId": "p"}),
        (
            "session",
            "other-session",
            {"id": "other-session", "instanceId": "i", "profileId": "other-profile"},
        ),
        ("turn", "t", {"id": "t", "sessionId": "s"}),
        ("turn", "other-turn", {"id": "other-turn", "sessionId": "other-session"}),
        ("tool_binding", "b", {"id": "b", "scope": {"instanceId": "i", "profileId": "p"}}),
        ("lease", "l", {"id": "l", "instanceId": "i"}),
        ("lease_slot", "i", {"leaseId": "l"}),
        ("tool_bundle", "bundle", {"id": "bundle"}),
    ]
    try:
        for kind, resource_id, payload in documents:
            await db.put(kind, resource_id, owner, payload)
            await db.put(kind, resource_id, other_owner, payload)
        await db.delete_runtime_tree(
            owner,
            instance_id="i",
            profile_id="p" if target != "instance" else None,
            session_id="s" if target == "session" else None,
        )
        for kind, resource_id, _ in documents:
            assert await db.get(kind, resource_id, other_owner) is not None
        assert await db.get("session", "s", owner) is None
        assert await db.get("turn", "t", owner) is None
        assert await db.get("instance", "other", owner) is not None
        assert await db.get("tool_bundle", "bundle", owner) is not None
        assert (await db.get("profile", "p", owner) is None) == (target != "session")
        assert (await db.get("tool_binding", "b", owner) is None) == (target != "session")
        assert (await db.get("instance", "i", owner) is None) == (target == "instance")
        assert (await db.get("session", "other-session", owner) is None) == (target == "instance")
        assert (await db.get("lease", "l", owner) is None) == (target == "instance")
        assert (await db.get("lease_slot", "i", owner) is None) == (target == "instance")
    finally:
        await db.close()
