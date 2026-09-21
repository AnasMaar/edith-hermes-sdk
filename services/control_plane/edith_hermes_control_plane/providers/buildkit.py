"""OCI image builder backed by Docker Buildx/BuildKit."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import shlex
import tempfile
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from ..config import Settings

LogCallback = Callable[[str], Awaitable[None]]
CancelCallback = Callable[[], Awaitable[bool]]
_PACKAGE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9+_.:@/=-]*$")
_TAG = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$")


@dataclass(frozen=True, slots=True)
class BuildArtifact:
    repository: str
    digest: str
    immutable_reference: str
    platforms: list[str]
    verification: dict[str, Any]


class BuildFailure(RuntimeError):
    pass


class BuildCancelled(BuildFailure):
    pass


class BuildKitProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def validate_recipe(self, recipe: dict[str, Any]) -> None:
        base = str(recipe.get("baseImage", ""))
        if not any(
            base.split("@", 1)[0].split(":", 1)[0] == allowed
            for allowed in self.settings.allowed_base_repositories
        ):
            raise BuildFailure("The base image repository is not allowed")
        if self.settings.require_digest_pinned_base and not re.search(
            r"@sha256:[a-f0-9]{64}$", base
        ):
            raise BuildFailure("Production image recipes require a digest-pinned base image")
        for artifact in recipe.get("artifacts") or []:
            if not re.fullmatch(r"sha256:[a-f0-9]{64}", str(artifact.get("checksum", ""))):
                raise BuildFailure("Production artifacts require a sha256 checksum")
            destination = str(artifact.get("destination", ""))
            if not re.fullmatch(
                r"/opt/hermes-extension/[A-Za-z0-9_./-]+", destination
            ) or ".." in destination.split("/"):
                raise BuildFailure("Artifacts may only be copied below /opt/hermes-extension/")
        if recipe.get("artifacts") and not self.settings.artifact_base_url:
            raise BuildFailure("EDITH_ARTIFACT_BASE_URL is required for artifact recipes")
        for family, packages in (recipe.get("packages") or {}).items():
            for package in packages or []:
                if not _PACKAGE.fullmatch(str(package)):
                    raise BuildFailure(f"Unsafe {family} package expression: {package!r}")

    @staticmethod
    def recipe_digest(recipe: dict[str, Any]) -> str:
        encoded = json.dumps(recipe, sort_keys=True, separators=(",", ":")).encode()
        return "sha256:" + hashlib.sha256(encoded).hexdigest()

    def dockerfile(self, recipe: dict[str, Any]) -> str:
        self.validate_recipe(recipe)
        packages = recipe.get("packages") or {}
        lines = ["# syntax=docker/dockerfile:1.7", f"FROM {recipe['baseImage']}"]
        apt = packages.get("apt") or []
        if apt:
            values = " ".join(shlex.quote(item) for item in apt)
            lines.append(
                "USER root\nRUN apt-get update && apt-get install -y --no-install-recommends "
                f"{values} && rm -rf /var/lib/apt/lists/*"
            )
        python = packages.get("python") or []
        if python:
            values = " ".join(shlex.quote(item) for item in python)
            lines.append(f"RUN /opt/hermes/.venv/bin/pip install --no-cache-dir {values}")
        node = packages.get("node") or []
        if node:
            values = " ".join(shlex.quote(item) for item in node)
            lines.append(f"RUN npm install --global --ignore-scripts {values}")
        for key, value in sorted((recipe.get("labels") or {}).items()):
            lines.append(f"LABEL {json.dumps(str(key))}={json.dumps(str(value))}")
        for index, artifact in enumerate(recipe.get("artifacts") or []):
            destination = str(artifact["destination"])
            mode = str(artifact.get("mode", "0644"))
            lines.append(f"COPY --chown=10000:10000 --chmod={mode} artifacts/{index} {destination}")
        runtime = recipe.get("runtime") or {}
        user = runtime.get("user", "10000:10000")
        lines.extend([f"USER {user}", "EXPOSE 9119", 'ENV HERMES_HOME="/opt/data"'])
        command = runtime.get("command")
        if command:
            lines.append("CMD " + json.dumps(command))
        else:
            lines.append('ENTRYPOINT ["/opt/hermes/.venv/bin/hermes"]')
            lines.append('CMD ["serve", "--host", "127.0.0.1", "--port", "9119"]')
        return "\n".join(lines) + "\n"

    async def _run(self, command: list[str], log: LogCallback, cancelled: CancelCallback) -> str:
        await log("$ " + " ".join(shlex.quote(item) for item in command))
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        output: list[str] = []
        assert process.stdout is not None
        while True:
            if await cancelled():
                process.terminate()
                await process.wait()
                raise BuildCancelled("Image build was cancelled")
            try:
                raw = await asyncio.wait_for(process.stdout.readline(), timeout=1)
            except TimeoutError:
                continue
            if not raw:
                break
            line = raw.decode(errors="replace").rstrip()
            output.append(line)
            await log(line)
        code = await process.wait()
        if code:
            raise BuildFailure(f"Command failed with exit code {code}: {command[0]}")
        return "\n".join(output)

    async def build(
        self,
        recipe: dict[str, Any],
        destination: dict[str, Any],
        build_secret_refs: list[str],
        log: LogCallback,
        cancelled: CancelCallback,
    ) -> BuildArtifact:
        self.validate_recipe(recipe)
        repository = str(destination["repository"])
        tags = destination.get("tags") or [self.recipe_digest(recipe).split(":", 1)[1][:16]]
        for tag in tags:
            if not _TAG.fullmatch(str(tag)):
                raise BuildFailure(f"Invalid OCI tag: {tag!r}")
        platforms = recipe.get("platforms") or ["linux/amd64"]
        with tempfile.TemporaryDirectory(prefix="edith-hermes-build-") as temp:
            context = Path(temp)
            await self._fetch_artifacts(recipe, context)
            (context / "Dockerfile").write_text(self.dockerfile(recipe), encoding="utf-8")
            metadata = context / "metadata.json"
            references = ",".join(f"{repository}:{tag}" for tag in tags)
            command = [
                self.settings.build_command,
                "--addr",
                self.settings.buildkit_address,
                "build",
                "--frontend",
                "dockerfile.v0",
                "--local",
                f"context={context}",
                "--local",
                f"dockerfile={context}",
            ]
            command.extend(
                [
                    "--opt",
                    "platform=" + ",".join(platforms),
                    "--output",
                    f"type=image,name={references},push=true",
                    "--attest",
                    "type=provenance,mode=max",
                    "--attest",
                    "type=sbom",
                    "--metadata-file",
                    str(metadata),
                ]
            )
            for key, value in sorted((recipe.get("buildArguments") or {}).items()):
                command.extend(["--opt", f"build-arg:{key}={value}"])
            for secret_ref in build_secret_refs:
                safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", secret_ref)
                secret_file = Path("/var/run/secrets/edith-build") / safe_name
                if not secret_file.is_file():
                    raise BuildFailure(f"Build secret is not mounted: {secret_ref}")
                command.extend(["--secret", f"id={safe_name},src={secret_file}"])
            await self._run(command, log, cancelled)
            values = json.loads(metadata.read_text(encoding="utf-8"))
            digest = values.get("containerimage.digest")
            if not isinstance(digest, str) or not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
                raise BuildFailure("BuildKit did not return an immutable image digest")
            immutable = f"{repository}@{digest}"
            verification: dict[str, Any] = {
                "status": "pending",
                "scanner": "trivy",
                "criticalVulnerabilities": 0,
                "highVulnerabilities": 0,
                "policyViolations": [],
            }
            if self.settings.require_image_scan:
                report = context / "trivy.json"
                await self._run(
                    [
                        self.settings.trivy_command,
                        "image",
                        "--format",
                        "json",
                        "--output",
                        str(report),
                        "--severity",
                        "HIGH,CRITICAL",
                        immutable,
                    ],
                    log,
                    cancelled,
                )
                scan = json.loads(report.read_text(encoding="utf-8"))
                severities = [
                    vulnerability.get("Severity")
                    for result in scan.get("Results") or []
                    for vulnerability in result.get("Vulnerabilities") or []
                ]
                verification["criticalVulnerabilities"] = severities.count("CRITICAL")
                verification["highVulnerabilities"] = severities.count("HIGH")
                if severities:
                    raise BuildFailure("Image policy rejected HIGH or CRITICAL vulnerabilities")
            if self.settings.require_image_signature:
                bundle = context / "cosign.bundle.json"
                await self._run(
                    [
                        self.settings.cosign_command,
                        "sign",
                        "--yes",
                        "--key",
                        self.settings.cosign_key,
                        "--bundle",
                        str(bundle),
                        immutable,
                    ],
                    log,
                    cancelled,
                )
            verification["status"] = "passed"
            return BuildArtifact(repository, digest, immutable, list(platforms), verification)

    async def _fetch_artifacts(self, recipe: dict[str, Any], context: Path) -> None:
        artifacts = recipe.get("artifacts") or []
        if not artifacts:
            return
        directory = context / "artifacts"
        directory.mkdir(mode=0o700)
        headers = (
            {"Authorization": f"Bearer {self.settings.artifact_bearer_token}"}
            if self.settings.artifact_bearer_token
            else {}
        )
        async with httpx.AsyncClient(timeout=120, follow_redirects=False) as client:
            for index, artifact in enumerate(artifacts):
                artifact_id = str(artifact["artifactId"])
                if not re.fullmatch(r"[A-Za-z0-9_.-]+", artifact_id):
                    raise BuildFailure(
                        "Artifact IDs may only contain letters, digits, '.', '_' and '-'"
                    )
                url = self.settings.artifact_base_url.rstrip("/") + "/" + artifact_id
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                if len(response.content) > self.settings.artifact_max_bytes:
                    raise BuildFailure(f"Artifact exceeds size limit: {artifact_id}")
                digest = "sha256:" + hashlib.sha256(response.content).hexdigest()
                if digest != artifact["checksum"]:
                    raise BuildFailure(f"Artifact checksum mismatch: {artifact_id}")
                (directory / str(index)).write_bytes(response.content)
