#!/usr/bin/env python3
"""Small, dependency-light structural validator for the Hermes SDK contracts."""

from __future__ import annotations

import hashlib
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: python -m pip install pyyaml") from exc


ROOT = Path(__file__).resolve().parents[1]
OPENAPI_DIR = ROOT / "contracts" / "openapi"
KUBERNETES_MANIFEST = ROOT / "deploy" / "kubernetes" / "hermes-pool.yaml"
HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def walk(value: Any, trail: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    yield trail, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, trail + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, trail + (str(index),))


def resolve_pointer(document: Any, pointer: str) -> Any:
    current = document
    for encoded in pointer.removeprefix("#/").split("/"):
        key = encoded.replace("~1", "/").replace("~0", "~")
        current = current[int(key)] if isinstance(current, list) else current[key]
    return current


def dereference_parameter(document: dict[str, Any], parameter: Any) -> Any:
    if isinstance(parameter, dict) and isinstance(parameter.get("$ref"), str):
        reference = parameter["$ref"]
        if reference.startswith("#/"):
            return resolve_pointer(document, reference)
    return parameter


def validate_openapi(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"cannot parse YAML: {exc}"]

    if not isinstance(document, dict):
        return ["root must be an object"]
    if document.get("openapi") != "3.1.0":
        errors.append("openapi must be exactly 3.1.0")
    if not isinstance(document.get("info"), dict) or not document["info"].get("title"):
        errors.append("info.title is required")
    paths = document.get("paths")
    if not isinstance(paths, dict) or not paths:
        errors.append("paths must be a non-empty object")
        return errors

    operation_ids: dict[str, str] = {}
    for route, path_item in paths.items():
        if not isinstance(route, str) or not route.startswith("/"):
            errors.append(f"invalid path key: {route!r}")
            continue
        if not isinstance(path_item, dict):
            errors.append(f"{route}: path item must be an object")
            continue
        placeholders = set(re.findall(r"\{([^{}]+)\}", route))
        path_parameters = list(path_item.get("parameters", []))
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS:
                continue
            location = f"{method.upper()} {route}"
            if not isinstance(operation, dict):
                errors.append(f"{location}: operation must be an object")
                continue
            operation_id = operation.get("operationId")
            if not operation_id:
                errors.append(f"{location}: operationId is required")
            elif operation_id in operation_ids:
                errors.append(
                    f"{location}: duplicate operationId {operation_id!r}; first used by "
                    f"{operation_ids[operation_id]}"
                )
            else:
                operation_ids[operation_id] = location
            parameters = path_parameters + list(operation.get("parameters", []))
            declared = {
                parameter.get("name")
                for raw in parameters
                if isinstance((parameter := dereference_parameter(document, raw)), dict)
                and parameter.get("in") == "path"
                and parameter.get("required") is True
            }
            missing = placeholders - declared
            if missing:
                errors.append(f"{location}: missing required path parameters {sorted(missing)}")
            if not isinstance(operation.get("responses"), dict) or not operation["responses"]:
                errors.append(f"{location}: responses are required")

    for trail, value in walk(document):
        if isinstance(value, dict) and isinstance(value.get("$ref"), str):
            reference = value["$ref"]
            if reference.startswith("#/"):
                try:
                    resolve_pointer(document, reference)
                except (KeyError, IndexError, TypeError, ValueError):
                    errors.append(f"{'/'.join(trail)}: unresolved reference {reference}")
    return errors


def validate_sources() -> list[str]:
    path = ROOT / "contracts" / "sources.yaml"
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"contracts/sources.yaml: cannot parse YAML: {exc}"]
    errors: list[str] = []
    for name, source in document.get("sdk", {}).items():
        relative = source.get("path") if isinstance(source, dict) else None
        if not relative:
            errors.append(f"contracts/sources.yaml: sdk.{name}.path is required")
            continue
        target = (path.parent / relative).resolve()
        if not target.is_file():
            errors.append(f"contracts/sources.yaml: sdk.{name}.path does not exist: {relative}")
    for name, source in document.get("upstream", {}).items():
        if not isinstance(source, dict) or not source.get("snapshot"):
            continue
        snapshot = (path.parent / source["snapshot"]).resolve()
        if not snapshot.is_file():
            errors.append(f"contracts/sources.yaml: upstream.{name}.snapshot does not exist")
            continue
        expected = str(source.get("sha256", "")).lower()
        actual = hashlib.sha256(snapshot.read_bytes()).hexdigest()
        if expected != actual:
            errors.append(f"contracts/sources.yaml: upstream.{name}.sha256 mismatch: {actual}")
    return errors


def validate_kubernetes_blueprint() -> list[str]:
    errors: list[str] = []
    try:
        documents = list(yaml.safe_load_all(KUBERNETES_MANIFEST.read_text(encoding="utf-8")))
    except Exception as exc:  # noqa: BLE001
        return [f"{KUBERNETES_MANIFEST.relative_to(ROOT)}: cannot parse YAML: {exc}"]
    resources = {
        (document.get("kind"), document.get("metadata", {}).get("name")): document
        for document in documents
        if isinstance(document, dict)
    }
    required = {
        ("Service", "hermes-pool-headless"),
        ("StatefulSet", "hermes-pool"),
        ("PodDisruptionBudget", "hermes-pool"),
        ("NetworkPolicy", "hermes-pool-ingress"),
    }
    missing = required - resources.keys()
    if missing:
        errors.append(f"Kubernetes blueprint is missing resources: {sorted(missing)}")
        return errors

    stateful_set = resources[("StatefulSet", "hermes-pool")]
    spec = stateful_set.get("spec", {})
    pod_spec = spec.get("template", {}).get("spec", {})
    labels = spec.get("template", {}).get("metadata", {}).get("labels", {})
    selector = spec.get("selector", {}).get("matchLabels", {})
    if not selector or any(labels.get(key) != value for key, value in selector.items()):
        errors.append("StatefulSet selector must match its pod-template labels")
    if spec.get("serviceName") != "hermes-pool-headless":
        errors.append("StatefulSet must use the headless pool Service")

    volume_names = {volume.get("name") for volume in pod_spec.get("volumes", [])}
    volume_names.update(
        claim.get("metadata", {}).get("name") for claim in spec.get("volumeClaimTemplates", [])
    )
    for container in pod_spec.get("containers", []):
        for mount in container.get("volumeMounts", []):
            if mount.get("name") not in volume_names:
                errors.append(f"Container volume mount is undeclared: {mount.get('name')}")
        security = container.get("securityContext", {})
        if security.get("allowPrivilegeEscalation") is not False:
            errors.append("Hermes container must disable privilege escalation")
    if pod_spec.get("securityContext", {}).get("runAsNonRoot") is not True:
        errors.append("Hermes pod must run as non-root")

    dockerfile = (ROOT / "deploy" / "image" / "Dockerfile").read_text(encoding="utf-8")
    for marker in (
        "nousresearch/hermes-agent",
        "USER 10000:10000",
        'ENTRYPOINT ["/opt/hermes/.venv/bin/hermes"]',
    ):
        if marker not in dockerfile:
            errors.append(f"Runtime Dockerfile is missing required marker: {marker}")
    return errors


def main() -> int:
    files = sorted(OPENAPI_DIR.glob("*.openapi.yaml"))
    errors = validate_sources() + validate_kubernetes_blueprint()
    titles: dict[str, Path] = {}
    for path in files:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        title = document.get("info", {}).get("title") if isinstance(document, dict) else None
        if title in titles:
            errors.append(f"{path.relative_to(ROOT)}: duplicate title also used by {titles[title]}")
        elif title:
            titles[title] = path.relative_to(ROOT)
        for error in validate_openapi(path):
            errors.append(f"{path.relative_to(ROOT)}: {error}")

    if errors:
        print("Contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Validated {len(files)} OpenAPI contracts, contracts/sources.yaml, "
        "and the Kubernetes runtime blueprint"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
