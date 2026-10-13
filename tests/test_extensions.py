import pytest

from edith_hermes import AsyncHermesExtensions


@pytest.mark.asyncio
async def test_versioned_extensions_have_explicit_profile_and_cas_identity():
    class Connection:
        def __init__(self): self.calls = []
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
    await client.update_mcp("server", revision="revision", patch={"enabled": False}, request_id="once")
    await client.mcp_operation("once")
    assert all(params["profile"] == "door" for _, params in connection.calls)
    assert connection.calls[2] == ("edith.desktop.v1.mcp.update", {"profile": "door", "name": "server", "revision": "revision", "patch": {"enabled": False}, "request_id": "once"})


@pytest.mark.asyncio
async def test_extension_version_and_unscoped_profiles_are_rejected():
    class Connection:
        async def call(self, *_args, **_params):return {"version": 2}
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
            return [{"status":"missing"}]
    client=AsyncHermesExtensions(Connection(),profile="door")
    requests=[{"path":"été.txt","objectId":None,"preferDisk":True}]
    assert await client.git_objects("C:/repo",requests,limit=100)==[{"status":"missing"}]
    assert calls[0][1]=={"profile":"door","path":"C:/repo","requests":requests,"limit":100}
    with pytest.raises(ValueError):
        await client.git_objects("C:/repo",requests,limit=0)
    with pytest.raises(ValueError):
        await client.git_objects("C:/repo",requests*33)
    assert len(calls)==1
