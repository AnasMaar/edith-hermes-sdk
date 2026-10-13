import json

import httpx
import pytest

from edith_hermes import AsyncHermesDesktop


@pytest.mark.asyncio
async def test_full_file_git_diff_uses_native_head_comparison_and_scope():
    def receive(request):
        assert request.url.path == "/api/git/file-diff"
        assert dict(request.url.params) == {"path": "C:/repo", "file": "été.txt", "profile": "door"}
        return httpx.Response(200, json={"diff": "staged and unstaged"})

    async with httpx.AsyncClient(
        base_url="http://hermes", transport=httpx.MockTransport(receive)
    ) as http:
        client = AsyncHermesDesktop.remote(
            base_url="http://hermes", profile="door", http_client=http
        )
        assert await client.git.file_diff("C:/repo", "été.txt") == "staged and unstaged"


@pytest.mark.asyncio
async def test_profile_scope_and_wire_contract():
    requests = []

    def receive(request):
        requests.append(request)
        if request.url.path.endswith("/runs"):
            return httpx.Response(200, json={"runs": [{"id": "run-1"}]})
        return httpx.Response(200, json={"id": "job-1", "profile": "door"})

    async with httpx.AsyncClient(
        base_url="http://hermes", transport=httpx.MockTransport(receive)
    ) as http:
        client = AsyncHermesDesktop.remote(
            base_url="http://hermes", profile="family", token="secret", http_client=http
        )
        door = client.for_profile("door")
        await door.cron.update("job-1", {"prompt": "Hello", "model": None})
        assert await door.cron.runs("job-1") == [{"id": "run-1"}]
        assert client.profile == "family"
        assert all(r.url.params["profile"] == "door" for r in requests)
        assert all(r.headers["authorization"] == "Bearer secret" for r in requests)
        assert json.loads(next(r for r in requests if r.method == "PUT").content) == {
            "updates": {"prompt": "Hello", "model": None}
        }
        await door.aclose()
        assert not http.is_closed


@pytest.mark.asyncio
async def test_uncertain_mutation_is_not_replayed():
    attempts = 0

    def receive(request):
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("Reply lost", request=request)

    async with httpx.AsyncClient(
        base_url="http://hermes", transport=httpx.MockTransport(receive)
    ) as http:
        client = AsyncHermesDesktop.remote(
            base_url="http://hermes", profile="family", http_client=http
        )
        with pytest.raises(httpx.ReadTimeout):
            await client.cron.trigger("job-1")
        assert attempts == 1


@pytest.mark.asyncio
async def test_cron_atomic_paused_creation_and_native_lifecycle():
    requests = []

    def receive(request):
        requests.append(request)
        return httpx.Response(200, json={"id": "new-job", "enabled": False, "profile": "door"})

    async with httpx.AsyncClient(
        base_url="http://hermes", transport=httpx.MockTransport(receive)
    ) as http:
        client = AsyncHermesDesktop.remote(
            base_url="http://hermes", profile="door", http_client=http
        )
        job = await client.cron.create(
            {
                "schedule": "every 1d",
                "name": "Paused",
                "paused": True,
                "script": "cert.py",
                "no_agent": True,
            }
        )
        assert not job["enabled"]
        await client.cron.resume(job["id"])
        await client.cron.pause(job["id"])
        await client.cron.remove(job["id"])
        assert [(r.method, r.url.path) for r in requests if r.method != "GET"] == [
            ("POST", "/api/cron/jobs"),
            ("POST", "/api/cron/jobs/new-job/resume"),
            ("POST", "/api/cron/jobs/new-job/pause"),
            ("DELETE", "/api/cron/jobs/new-job"),
        ]
        assert json.loads(requests[0].content)["paused"] is True
        assert all(r.url.params["profile"] == "door" for r in requests)


@pytest.mark.asyncio
async def test_discovery_uses_real_operations_and_encoded_ids():
    requests = []

    def receive(request):
        requests.append(request)
        if request.url.path == "/openapi.json":
            return httpx.Response(
                200, json={"paths": {"/api/cron/jobs": {"get": {}, "parameters": []}}}
            )
        return httpx.Response(200, json={"id": "job", "profile": "family"})

    async with httpx.AsyncClient(
        base_url="http://hermes", transport=httpx.MockTransport(receive)
    ) as http:
        client = AsyncHermesDesktop.remote(
            base_url="http://hermes", profile="family", http_client=http
        )
        assert (await client.capabilities())["operations"] == ["GET /api/cron/jobs"]
        await client.cron.get("a/b ?#")
        assert b"a%2Fb%20%3F%23" in requests[-1].url.raw_path
        with pytest.raises(ValueError):
            await client.cron.get("..")


@pytest.mark.parametrize("profile", ["", "all", "ALL", " all", "family "])
def test_concrete_profile_required(profile):
    with pytest.raises(ValueError):
        AsyncHermesDesktop.remote(base_url="http://hermes", profile=profile)


@pytest.mark.asyncio
async def test_cron_fallback_owner_is_rejected_before_a_mutation():
    requests = []

    def receive(request):
        requests.append(request)
        return httpx.Response(200, json={"id": "other-job", "profile": "door"})

    async with httpx.AsyncClient(
        base_url="http://hermes", transport=httpx.MockTransport(receive)
    ) as http:
        client = AsyncHermesDesktop.remote(
            base_url="http://hermes", profile="family", http_client=http
        )
        for mutate in (
            client.cron.pause,
            client.cron.resume,
            client.cron.remove,
            client.cron.trigger,
        ):
            with pytest.raises(ValueError, match="another profile"):
                await mutate("other-job")
        with pytest.raises(ValueError, match="another profile"):
            await client.cron.update("other-job", {"prompt": "overwrite"})
        assert all(r.method == "GET" for r in requests)


@pytest.mark.asyncio
async def test_history_checks_returned_owner_and_bounds():
    def receive(request):
        assert request.url.params["profile"] == "family"
        assert request.url.params["inline_images"] == "false"
        return httpx.Response(200, json={"profile": "door", "messages": []})

    async with httpx.AsyncClient(
        base_url="http://hermes", transport=httpx.MockTransport(receive)
    ) as http:
        client = AsyncHermesDesktop.remote(
            base_url="http://hermes", profile="family", http_client=http
        )
        with pytest.raises(ValueError, match="another profile"):
            await client.sessions.messages("same-id")
        with pytest.raises(ValueError, match="between 1 and 500"):
            await client.sessions.messages("same-id", limit=501)


@pytest.mark.asyncio
async def test_http_body_cannot_override_owning_profile():
    async with httpx.AsyncClient(base_url="http://hermes") as http:
        client = AsyncHermesDesktop.remote(
            base_url="http://hermes", profile="family", http_client=http
        )
        with pytest.raises(ValueError, match="bound profile"):
            await client.configure({"profile": "door", "config": {"model": {"default": "other"}}})


@pytest.mark.asyncio
async def test_skills_hub_uses_native_routes_exact_wire_shapes_and_concrete_profile():
    requests = []

    def receive(request):
        requests.append(request)
        if request.url.path == "/api/skills" and request.method == "GET":
            return httpx.Response(
                200, json=[{"name": "research", "enabled": True, "usage": 2, "provenance": "hub"}]
            )
        if request.url.path.endswith("/official"):
            return httpx.Response(
                200, json={"skills": [{"identifier": "official/research", "name": "research"}]}
            )
        if request.url.path.endswith("/search"):
            return httpx.Response(
                200, json={"results": [], "source_counts": {}, "timed_out": [], "installed": {}}
            )
        if request.url.path.endswith("/scan"):
            return httpx.Response(
                200, json={"identifier": "official/research", "policy": "ask", "findings": []}
            )
        if request.url.path.endswith(("/install", "/uninstall", "/update")):
            return httpx.Response(200, json={"ok": True, "pid": 123, "name": "native-hub-action"})
        return httpx.Response(
            200,
            json={
                "ok": True,
                "name": "research",
                "content": "Native skill",
                "path": "/door/skills/research/SKILL.md",
            },
        )

    async with httpx.AsyncClient(
        base_url="http://hermes", transport=httpx.MockTransport(receive)
    ) as http:
        client = AsyncHermesDesktop.remote(
            base_url="http://hermes", profile="door", token="backend-token", http_client=http
        )
        assert (await client.skills.list())[0]["usage"] == 2
        assert (await client.skills.official())[0]["identifier"] == "official/research"
        assert (await client.skills.content("research"))["content"] == "Native skill"
        await client.skills.save("research", "Edited skill")
        await client.skills.create("new", "Created skill", category="tools")
        await client.skills.toggle("research", False)
        await client.skills.search("notes", source="official", limit=50)
        await client.skills.preview("official/research")
        assert (await client.skills.scan("official/research"))["policy"] == "ask"
        assert (await client.skills.install("official/research"))["pid"] == 123
        await client.skills.uninstall("research")
        await client.skills.update()
        assert all(
            request.url.params["profile"] == "door"
            and request.headers["authorization"] == "Bearer backend-token"
            for request in requests
        )
        assert json.loads(
            next(request.content for request in requests if request.url.path.endswith("/toggle"))
        ) == {"name": "research", "enabled": False}
        assert json.loads(
            next(request.content for request in requests if request.url.path.endswith("/install"))
        ) == {"identifier": "official/research"}
        assert (
            next(
                request for request in requests if request.url.path.endswith("/search")
            ).url.params["q"]
            == "notes"
        )
        with pytest.raises(ValueError, match="between 1 and 50"):
            await client.skills.search("notes", limit=51)


@pytest.mark.asyncio
async def test_lost_skill_installer_receipt_is_never_replayed_by_sdk():
    requests = []

    def receive(request):
        requests.append(request)
        raise httpx.ReadTimeout("Installer started but receipt lost", request=request)

    async with httpx.AsyncClient(
        base_url="http://hermes", transport=httpx.MockTransport(receive)
    ) as http:
        client = AsyncHermesDesktop.remote(
            base_url="http://hermes", profile="family", http_client=http
        )
        with pytest.raises(httpx.ReadTimeout):
            await client.skills.install("official/research")
        assert len(requests) == 1
