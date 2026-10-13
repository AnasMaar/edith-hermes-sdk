import pytest

from edith_hermes import AsyncHermesExtensions


@pytest.mark.asyncio
async def test_skills_inventory_and_enablement_have_explicit_profile_and_revision():
    calls = []
    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return {'skills': []} if method.endswith('inventory') else {'id': 'stable', 'enabled': False}
    client = AsyncHermesExtensions(Connection(), profile='door')
    assert await client.skill_inventory() == []
    assert (await client.toggle_skill('stable', revision='before', enabled=False))['enabled'] is False
    assert calls == [('edith.desktop.v1.skills.inventory', {'profile': 'door'}),
                     ('edith.desktop.v1.skills.toggle', {'profile': 'door', 'id': 'stable', 'revision': 'before', 'enabled': False})]


@pytest.mark.asyncio
async def test_blueprint_preparation_is_profile_scoped_and_never_creates_a_job():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return {
                "profile": "family",
                "schedule": "0 9 * * 1-5",
                "prompt": "Prepared native instructions",
            }

    client = AsyncHermesExtensions(Connection(), profile="family")
    assert (await client.prepare_blueprint("morning", {"time": "09:00"}))[
        "schedule"
    ] == "0 9 * * 1-5"
    assert calls == [
        (
            "edith.desktop.v1.cron.prepare",
            {"profile": "family", "blueprint": "morning", "values": {"time": "09:00"}},
        )
    ]
    with pytest.raises(ValueError, match="another profile"):
        await AsyncHermesExtensions(Connection(), profile="door").prepare_blueprint("morning", {})


@pytest.mark.asyncio
async def test_versioned_extensions_have_explicit_profile_and_cas_identity():
    class Connection:
        def __init__(self):
            self.calls = []

        async def call(self, method, **params):
            self.calls.append((method, params))
            if method.endswith("capabilities"):
                return {"version": 1, "operations": ["mcp.update"]}
            if method.endswith("revisions"):
                return {"revisions": {"server": "revision"}}
            return {"status": "applied"}

    connection = Connection()
    client = AsyncHermesExtensions(connection, profile="door")
    assert (await client.capabilities())["version"] == 1
    assert await client.mcp_revisions() == {"server": "revision"}
    await client.update_mcp(
        "server", revision="revision", patch={"enabled": False}, request_id="once"
    )
    await client.mcp_operation("once")
    assert all(params["profile"] == "door" for _, params in connection.calls)
    assert connection.calls[2] == (
        "edith.desktop.v1.mcp.update",
        {
            "profile": "door",
            "name": "server",
            "revision": "revision",
            "patch": {"enabled": False},
            "request_id": "once",
        },
    )


@pytest.mark.asyncio
async def test_extension_version_and_unscoped_profiles_are_rejected():
    class Connection:
        async def call(self, *_args, **_params):
            return {"version": 2}

    with pytest.raises(ValueError):
        AsyncHermesExtensions(Connection(), profile="all")
    with pytest.raises(ValueError, match="version"):
        await AsyncHermesExtensions(Connection(), profile="family").capabilities()


@pytest.mark.asyncio
async def test_git_metadata_binding_retains_host_path_and_profile():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return None

    client = AsyncHermesExtensions(Connection(), profile="family")
    assert await client.git_inspect("C:/été/repo") is None
    assert calls == [("edith.desktop.v1.git.inspect", {"profile": "family", "path": "C:/été/repo"})]


@pytest.mark.asyncio
async def test_git_object_reads_are_bounded_and_profile_scoped():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return [{"status": "missing"}]

    client = AsyncHermesExtensions(Connection(), profile="door")
    requests = [{"path": "été.txt", "objectId": None, "preferDisk": True}]
    assert await client.git_objects("C:/repo", requests, limit=100) == [{"status": "missing"}]
    assert calls[0][1] == {"profile": "door", "path": "C:/repo", "requests": requests, "limit": 100}
    with pytest.raises(ValueError):
        await client.git_objects("C:/repo", requests, limit=0)
    with pytest.raises(ValueError):
        await client.git_objects("C:/repo", requests * 33)
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_native_review_patch_and_cron_receipt_bindings_do_not_retry():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return (
                {"diff": "byte-faithful\r\n"} if method.endswith("diff") else {"status": "running"}
            )

    client = AsyncHermesExtensions(Connection(), profile="family")
    await client.git_apply("C:/repo", "patch", target="staged", reverse=True)
    await client.cron_trigger("job", request_id="request")
    await client.cron_operation("request")
    assert await client.git_diff("C:/repo", "été.txt", source="unstaged") == "byte-faithful\r\n"
    assert calls == [
        (
            "edith.desktop.v1.git.apply",
            {
                "profile": "family",
                "path": "C:/repo",
                "diff": "patch",
                "target": "staged",
                "reverse": True,
            },
        ),
        (
            "edith.desktop.v1.cron.trigger",
            {"profile": "family", "job_id": "job", "request_id": "request"},
        ),
        ("edith.desktop.v1.cron.operation", {"profile": "family", "request_id": "request"}),
        (
            "edith.desktop.v1.git.diff",
            {"profile": "family", "path": "C:/repo", "file": "été.txt", "source": "unstaged"},
        ),
    ]
    with pytest.raises(ValueError):
        await client.git_apply("C:/repo", "", target="unstaged")


@pytest.mark.asyncio
async def test_group_tool_activity_retains_room_and_profile_scope():
    calls = []

    class Connection:
        async def call(self, method, **params):
            calls.append((method, params))
            return {"tools": []}

    assert await AsyncHermesExtensions(Connection(), profile="door").group_activity("room") == []
    assert calls == [("edith.desktop.v1.groups.activity", {"profile": "door", "room_id": "room"})]
