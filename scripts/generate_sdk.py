#!/usr/bin/env python3
"""Generate deterministic namespace clients from SDK OpenAPI and Hermes OpenRPC."""

from __future__ import annotations

import json
import keyword
import pprint
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
OPENAPI_DIR = ROOT / "contracts" / "openapi"
OPENRPC_PATH = ROOT / "contracts" / "vendor" / "hermes" / "gateway-contract.openrpc.json"
INFERENCE_PATH = ROOT / "contracts" / "vendor" / "nous" / "inference.openapi.json"
OUTPUT = ROOT / "src" / "edith_hermes" / "generated"
HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
NAMESPACES = {
    "control-plane.openapi.yaml": ("control_plane", "AsyncControlPlaneAPI"),
    "images.openapi.yaml": ("images", "AsyncImagesAPI"),
    "runtime.openapi.yaml": ("runtime", "AsyncRuntimeAPI"),
    "tools.openapi.yaml": ("tools", "AsyncToolsAPI"),
}


def snake(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    if not value:
        value = "invoke"
    if value[0].isdigit() or keyword.iskeyword(value):
        value = f"method_{value}"
    return value


def resolve(document: dict[str, Any], value: Any) -> Any:
    if not isinstance(value, dict) or not str(value.get("$ref", "")).startswith("#/"):
        return value
    current: Any = document
    for token in value["$ref"][2:].split("/"):
        current = current[token.replace("~1", "/").replace("~0", "~")]
    return current


def openapi_operations(path: Path, namespace: str) -> list[dict[str, Any]]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    operations: list[dict[str, Any]] = []
    for route, item in document["paths"].items():
        common = list(item.get("parameters", []))
        for method, operation in item.items():
            if method not in HTTP_METHODS:
                continue
            parameters = [
                resolve(document, item) for item in common + operation.get("parameters", [])
            ]
            path_parameters = [
                parameter["name"]
                for parameter in parameters
                if isinstance(parameter, dict) and parameter.get("in") == "path"
            ]
            query_parameters = [
                parameter["name"]
                for parameter in parameters
                if isinstance(parameter, dict) and parameter.get("in") == "query"
            ]
            header_parameters = [
                parameter["name"]
                for parameter in parameters
                if isinstance(parameter, dict) and parameter.get("in") == "header"
            ]
            streaming = any(
                "text/event-stream" in response.get("content", {})
                for response in operation.get("responses", {}).values()
                if isinstance(response, dict)
            )
            operations.append(
                {
                    "namespace": namespace,
                    "operation_id": operation["operationId"],
                    "python_name": snake(operation["operationId"]),
                    "method": method.upper(),
                    "path": route,
                    "path_parameters": path_parameters,
                    "query_parameters": query_parameters,
                    "header_parameters": header_parameters,
                    "streaming": streaming,
                }
            )
    return operations


def render_operations(all_operations: list[dict[str, Any]], rpc_methods: list[str]) -> str:
    payload = pprint.pformat(all_operations, sort_dicts=True, width=100)
    rpc_payload = pprint.pformat(rpc_methods, sort_dicts=False, width=100)
    return (
        '"""Generated operation metadata. Do not edit."""\n\n'
        "from __future__ import annotations\n\n"
        f"OPERATIONS = {payload}\n\n"
        "BY_ID = {item['operation_id']: item for item in OPERATIONS}\n\n"
        f"HERMES_RPC_METHODS = {rpc_payload}\n"
    )


def render_namespaces(grouped: dict[str, tuple[str, list[dict[str, Any]]]], rpc: list[str]) -> str:
    lines = [
        '"""Generated namespace clients. Do not edit."""',
        "",
        "from __future__ import annotations",
        "",
        "from collections.abc import AsyncIterator, Mapping",
        "from typing import Any",
        "",
        "from ..transport import AsyncTransport",
        "from .operations import BY_ID, HERMES_RPC_METHODS",
        "",
        "",
        "class _AsyncAPI:",
        "    def __init__(self, transport: AsyncTransport):",
        "        self._transport = transport",
        "",
    ]
    for _, (class_name, operations) in sorted(grouped.items()):
        lines.extend(["", f"class {class_name}(_AsyncAPI):"])
        if not operations:
            lines.append("    pass")
            continue
        for operation in operations:
            name = operation["python_name"]
            operation_id = operation["operation_id"]
            if operation["streaming"]:
                lines.extend(
                    [
                        f"    def {name}(self, **arguments: Any) -> AsyncIterator[dict[str, Any]]:",
                        f"        return self._transport.stream(BY_ID[{operation_id!r}], arguments)",
                    ]
                )
            else:
                lines.extend(
                    [
                        f"    async def {name}(self, **arguments: Any) -> Any:",
                        f"        return await self._transport.invoke(BY_ID[{operation_id!r}], arguments)",
                    ]
                )
            lines.append("")

    rpc_operation = {
        "operation_id": "invokeHermesRpc",
        "method": "POST",
        "path": "/v1/instances/{instanceId}/profiles/{profileId}/rpc",
        "path_parameters": ["instanceId", "profileId"],
        "query_parameters": [],
        "header_parameters": [],
    }
    lines.extend(
        [
            "",
            "class AsyncGatewayAPI(_AsyncAPI):",
            f"    _operation: Mapping[str, Any] = {rpc_operation!r}",
            "    methods = tuple(HERMES_RPC_METHODS)",
            "",
            "    async def invoke(",
            "        self, method: str, *, instance_id: str, profile_id: str, params: Any = None",
            "    ) -> Any:",
            "        request = {'jsonrpc': '2.0', 'id': 1, 'method': method}",
            "        if params is not None:",
            "            request['params'] = params",
            "        return await self._transport.invoke(",
            "            self._operation,",
            "            {'instance_id': instance_id, 'profile_id': profile_id, 'body': request},",
            "        )",
            "",
        ]
    )
    counts = Counter(snake(name) for name in rpc)
    used: Counter[str] = Counter()
    for method in rpc:
        base = snake(method)
        used[base] += 1
        name = base if counts[base] == 1 else f"{base}_{used[base]}"
        lines.extend(
            [
                f"    async def {name}(",
                "        self, *, instance_id: str, profile_id: str, **params: Any",
                "    ) -> Any:",
                f"        return await self.invoke({method!r}, instance_id=instance_id, profile_id=profile_id, params=params)",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    all_operations: list[dict[str, Any]] = []
    grouped: dict[str, tuple[str, list[dict[str, Any]]]] = {}
    for filename, (namespace, class_name) in NAMESPACES.items():
        operations = openapi_operations(OPENAPI_DIR / filename, namespace)
        all_operations.extend(operations)
        grouped[namespace] = (class_name, operations)

    inference_operations = openapi_operations(INFERENCE_PATH, "inference")
    inference_names = {
        "/chat/completions": ("createChatCompletion", "create_chat_completion"),
        "/completions": ("createCompletion", "create_completion"),
    }
    for operation in inference_operations:
        original_path = operation["path"]
        operation["path"] = "/v1/inference" + original_path
        operation["operation_id"], operation["python_name"] = inference_names[original_path]
    all_operations.extend(inference_operations)
    grouped["inference"] = ("AsyncInferenceAPI", inference_operations)

    openrpc = json.loads(OPENRPC_PATH.read_text(encoding="utf-8"))
    rpc_methods = [method["name"] for method in openrpc.get("methods", [])]
    (OUTPUT / "operations.py").write_text(
        render_operations(all_operations, rpc_methods), encoding="utf-8", newline="\n"
    )
    (OUTPUT / "namespaces.py").write_text(
        render_namespaces(grouped, rpc_methods), encoding="utf-8", newline="\n"
    )
    print(f"Generated {len(all_operations)} HTTP operations and {len(rpc_methods)} RPC methods")


if __name__ == "__main__":
    main()
