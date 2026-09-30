"""Generate the discoverable convenience API from the same pinned contracts.

Typing describes the wire contract; it intentionally does not validate server responses.
Unknown JSON and open extension maps remain Any, never invented restrictive schemas.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

# operation -> (resource, Python method). Explicit naming makes changes reviewable;
# exact-set coverage below makes an unmapped new contract operation a build failure.
ROUTES = {
    "getControlPlaneCapabilities": ("Root", "capabilities"),
    "listInstances": ("Instances", "list"),
    "createInstance": ("Instances", "create"),
    "getInstance": ("Instance", "get"),
    "updateInstance": ("Instance", "update"),
    "deleteInstance": ("Instance", "delete"),
    "changeInstanceState": ("Instance", "action"),
    "getInstanceConnection": ("Instance", "connection"),
    "getInstanceCapabilities": ("Instance", "capabilities"),
    "getInstanceRuntimeCapabilities": ("Instance", "runtime_capabilities"),
    "listProfiles": ("Profiles", "list"),
    "createProfile": ("Profiles", "create"),
    "getProfile": ("Profile", "get"),
    "updateProfile": ("Profile", "update"),
    "deleteProfile": ("Profile", "delete"),
    "listPools": ("Pools", "list"),
    "createPool": ("Pools", "create"),
    "getPool": ("Pool", "get"),
    "updatePool": ("Pool", "update"),
    "deletePool": ("Pool", "delete"),
    "acquireInstanceLease": ("Leases", "acquire"),
    "releaseInstanceLease": ("Lease", "release"),
    "provisionUserInstance": ("Jobs", "create"),
    "getProvisioningJob": ("Job", "get"),
    "listImageRecipes": ("Recipes", "list"),
    "createImageRecipe": ("Recipes", "create"),
    "getImageRecipe": ("Recipe", "get"),
    "deleteImageRecipe": ("Recipe", "delete"),
    "listImageBuilds": ("Builds", "list"),
    "startImageBuild": ("Builds", "start"),
    "getImageBuild": ("Build", "get"),
    "cancelImageBuild": ("Build", "cancel"),
    "streamImageBuildLogs": ("Build", "logs"),
    "listManagedImages": ("Images", "list"),
    "getManagedImage": ("Image", "get"),
    "deleteManagedImage": ("Image", "delete"),
    "listSessions": ("Sessions", "list"),
    "createSession": ("Sessions", "create"),
    "getSession": ("Session", "get"),
    "deleteSession": ("Session", "delete"),
    "actOnSession": ("Session", "action"),
    "submitTurn": ("Turns", "submit"),
    "getTurn": ("Turn", "get"),
    "actOnTurn": ("Turn", "action"),
    "streamSessionEvents": ("Session", "events"),
    "invokeHermesRpc": ("Profile", "request"),
    "listToolBundles": ("Bundles", "list"),
    "createToolBundle": ("Bundles", "create"),
    "getToolBundle": ("Bundle", "get"),
    "replaceToolBundle": ("Bundle", "replace"),
    "deleteToolBundle": ("Bundle", "delete"),
    "listToolBindings": ("Bindings", "list"),
    "createToolBinding": ("Bindings", "create"),
    "getToolBinding": ("Binding", "get"),
    "deleteToolBinding": ("Binding", "delete"),
    "listMcpServers": ("McpServers", "list"),
    "createMcpServer": ("McpServers", "create"),
    "getMcpServer": ("McpServer", "get"),
    "replaceMcpServer": ("McpServer", "replace"),
    "deleteMcpServer": ("McpServer", "delete"),
    "actOnMcpServer": ("McpServer", "action"),
    "executeToolCall": ("Tools", "call"),
    "createChatCompletion": ("Inference", "chat"),
    "createCompletion": ("Inference", "complete"),
    "listAuthProviders": ("Providers", "list"),
    "getAuthProvider": ("Provider", "status"),
    "disconnectAuthProvider": ("Provider", "disconnect"),
    "startProviderLogin": ("ProviderLogins", "start"),
    "getProviderLogin": ("ProviderLogin", "get"),
    "cancelProviderLogin": ("ProviderLogin", "cancel"),
    "listProviderAccounts": ("ProviderAccounts", "list"),
    "removeProviderAccount": ("ProviderAccount", "remove"),
}
CHILDREN = {
    "Root": {
        "instances": "Instances",
        "pools": "Pools",
        "jobs": "Jobs",
        "images": "Images",
        "tools": "Tools",
        "inference": "Inference",
    },
    "Instance": {"profiles": "Profiles"},
    "Profile": {"sessions": "Sessions", "native": "Native", "providers": "Providers"},
    "Provider": {"logins": "ProviderLogins", "accounts": "ProviderAccounts"},
    "Session": {"turns": "Turns"},
    "Pool": {"leases": "Leases"},
    "Images": {"recipes": "Recipes", "builds": "Builds"},
    "Tools": {"bundles": "Bundles", "bindings": "Bindings", "mcp_servers": "McpServers"},
}
COLLECTIONS = {
    "Instances": ("Instance", "instance_id"),
    "Profiles": ("Profile", "profile_id"),
    "Sessions": ("Session", "session_id"),
    "Turns": ("Turn", "turn_id"),
    "Pools": ("Pool", "pool_id"),
    "Leases": ("Lease", "lease_id"),
    "Jobs": ("Job", "job_id"),
    "Images": ("Image", "image_id"),
    "Recipes": ("Recipe", "recipe_id"),
    "Builds": ("Build", "build_id"),
    "Bundles": ("Bundle", "bundle_id"),
    "Bindings": ("Binding", "binding_id"),
    "McpServers": ("McpServer", "server_id"),
    "Providers": ("Provider", "provider_id"),
    "ProviderLogins": ("ProviderLogin", "login_id"),
    "ProviderAccounts": ("ProviderAccount", "account_index"),
}


def generate(root: Path, operations: list[dict[str, Any]]) -> None:
    from generate_sdk import NAMESPACES, resolve, snake

    output = root / "src/edith_hermes/generated"
    docs = {
        ns: yaml.safe_load((root / "contracts/openapi" / filename).read_text(encoding="utf-8"))
        for filename, (ns, _) in NAMESPACES.items()
    }
    docs["inference"] = json.loads(
        (root / "contracts/vendor/nous/inference.openapi.json").read_text()
    )
    docs["native"] = json.loads(
        (root / "contracts/vendor/hermes/gateway-contract.openrpc.json").read_text()
    )
    models: dict[str, dict[str, str]] = defaultdict(dict)

    def merged(ns: str, schema: Any) -> Any:
        schema = resolve(docs[ns], schema)
        if not isinstance(schema, dict) or "allOf" not in schema:
            return schema
        parts = [merged(ns, p) for p in schema["allOf"]]
        if not all(isinstance(p, dict) for p in parts):
            raise ValueError("Unsupported allOf")
        result = {k: v for k, v in schema.items() if k != "allOf"}
        result["type"] = "object"
        result["properties"] = {
            **schema.get("properties", {}),
            **{k: v for p in parts for k, v in p.get("properties", {}).items()},
        }
        result["required"] = sorted(
            set(schema.get("required", [])) | {k for p in parts for k in p.get("required", [])}
        )
        return result

    def type_of(ns: str, schema: Any, name: str, *, definition: bool = False) -> str:
        if not isinstance(schema, dict):
            return "Any"
        if "$ref" in schema and not definition:
            if not schema["$ref"].startswith("#"):
                filename, ref = schema["$ref"].split("#", 1)
                target_ns = NAMESPACES[Path(filename).name][0]
                return f"types_{target_ns}." + ref.split("/")[-1]
            return schema["$ref"].split("/")[-1]
        schema = merged(ns, schema)
        props = schema.get("properties")
        if props is not None:
            if name not in models[ns]:
                models[ns][name] = ""  # recursive references
                fields = []
                for key, value in props.items():
                    annotation = type_of(ns, value, name + pascal(key))
                    if key in schema.get("required", []):
                        encoded = f"Required[{annotation!r}]"
                    else:
                        encoded = repr(annotation)
                    fields.append(f"    {key!r}: {encoded},")
                models[ns][name] = (
                    f"{name} = TypedDict({name!r}, {{\n" + "\n".join(fields) + "\n}, total=False)\n"
                )
            return name
        choices = schema.get("oneOf", schema.get("anyOf"))
        if choices:
            types = [type_of(ns, p, name + str(i)) for i, p in enumerate(choices)]
            return "Union[" + ", ".join(dict.fromkeys(types)) + "]"
        if "const" in schema or "enum" in schema:
            values = schema.get("enum", [schema.get("const")])
            if all(isinstance(v, (str, bool, int)) or v is None for v in values):
                return "Literal[" + ", ".join(repr(v) for v in values) + "]"
        kind = schema.get("type")
        if isinstance(kind, list):
            return (
                "Union[" + ", ".join(type_of(ns, {**schema, "type": k}, name) for k in kind) + "]"
            )
        if kind == "array":
            return f"builtins.list[{type_of(ns, schema.get('items', {}), name + 'Item')}]"
        if kind == "object":
            return (
                f"dict[str, {type_of(ns, schema.get('additionalProperties', {}), name + 'Value')}]"
            )
        return {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "null": "None",
        }.get(kind, "Any")

    def pascal(value: str) -> str:
        return "".join(p.capitalize() for p in snake(value).split("_"))

    # Define all named schemas, including non-object aliases.
    for ns, doc in docs.items():
        for name, schema in doc.get("components", {}).get("schemas", {}).items():
            annotation = type_of(ns, schema, name, definition=True)
            if name not in models[ns]:
                # Evaluate aliases after object declarations (forward refs within unions are quoted).
                models[ns][name] = f"{name}: TypeAlias = {annotation}\n"

    def qualified(ns: str, annotation: str) -> str:
        # Resolve local model names in signature annotations, including forward refs.
        import re

        return re.sub(
            r"\b[A-Za-z_]\w*\b",
            lambda m: f"_types_{ns}.{m[0]}" if m[0] in models[ns] else m[0],
            annotation,
        )

    def parameters(
        ns: str, schema: Any, name: str, skip: set[str] | None = None
    ) -> tuple[list[str], dict[str, str]]:
        schema = merged(ns, schema)
        fields, values = [], {}
        for wire, prop in schema.get("properties", {}).items():
            if wire in (skip or set()):
                continue
            arg = snake(wire)
            if arg in {"self", "extra_body", "extra_params"}:
                arg = "field_" + arg
            annotation = qualified(ns, type_of(ns, prop, name + pascal(wire)))
            required = wire in schema.get("required", [])
            fields.append(f"{arg}: {annotation}" + ("" if required else " | Unset = UNSET"))
            values[wire] = arg
        return fields, values

    def dict_code(values: dict[str, str]) -> str:
        return "{" + ", ".join(f"{k!r}: {v}" for k, v in values.items()) + "}"

    classes: dict[str, list[str]] = defaultdict(list)
    coverage: dict[str, str] = {}
    if set(ROUTES) != {o["operation_id"] for o in operations}:
        raise ValueError("Convenience routes and contract operations differ; update ROUTES")
    for operation in operations:
        op_id, ns = operation["operation_id"], operation["namespace"]
        cls, method = ROUTES[op_id]
        coverage[op_id] = f"{cls}Resource.{method}"
        route = (
            operation["path"].removeprefix("/v1/inference")
            if ns == "inference"
            else operation["path"]
        )
        item = docs[ns]["paths"][route]
        op = item[operation["method"].lower()]
        args, values = [], {}
        for p in item.get("parameters", []) + op.get("parameters", []):
            p = resolve(docs[ns], p)
            if p["in"] == "path" and p["name"] != "action":
                continue
            arg = snake(p["name"])
            annotation = qualified(ns, type_of(ns, p.get("schema", {}), op_id + pascal(arg)))
            required = p.get("required") and p["name"] != "Idempotency-Key"
            args.append(f"{arg}: {annotation}" + ("" if required else " | Unset = UNSET"))
            values[arg] = arg
        body = resolve(docs[ns], op.get("requestBody", {}))
        schema = next(
            (
                media.get("schema")
                for kind, media in body.get("content", {}).items()
                if "json" in kind
            ),
            None,
        )
        setup = []
        if schema is not None:
            expanded = merged(ns, schema)
            if isinstance(expanded, dict) and "properties" in expanded:
                fields, body_values = parameters(ns, schema, op_id)
                args.extend(fields)
                args.append("extra_body: Mapping[str, Any] | None = None")
                setup.append(f"        body = _payload({dict_code(body_values)}, extra_body)")
            else:
                annotation = qualified(ns, type_of(ns, schema, op_id + "Body"))
                args.append(
                    f"body: {annotation}" + ("" if body.get("required") else " | Unset = UNSET")
                )
            values["body"] = "body"
        response_type = "Any"
        for code, response in op.get("responses", {}).items():
            if str(code).startswith("2"):
                response = resolve(docs[ns], response)
                s = response.get("content", {}).get("application/json", {}).get("schema")
                if s is not None:
                    response_type = qualified(ns, type_of(ns, s, op_id + "Result"))
                break
        signature = "self" + (", *, " + ", ".join(args) if args else "")
        if operation["streaming"]:
            lines = [f"    def {method}({signature}) -> AsyncIterator[dict[str, Any]]:"]
            lines.extend(setup)
            lines.append(f"        return self._stream({op_id!r}, _payload({dict_code(values)}))")
        else:
            lines = [f"    async def {method}({signature}) -> {response_type}:"]
            lines.extend(setup)
            call = f"await self._invoke({op_id!r}, _payload({dict_code(values)}))"
            if cls == "ProviderLogin":
                call = f"self._remember({call})"
            lines.append(
                f"        return {call}"
                if response_type == "Any" or cls == "ProviderLogin"
                else f"        return typing.cast({response_type!r}, {call})"
            )
        classes[cls].extend(lines + [""])

    native_coverage = {}
    for method in docs["native"]["methods"]:
        parts = method["name"].split(".")
        parent = "Native"
        for part in parts[:-1]:
            child = parent + pascal(part)
            CHILDREN.setdefault(parent, {})[snake(part)] = child
            parent = child
        method_name = snake(parts[-1])
        if any(m["name"].startswith(method["name"] + ".") for m in docs["native"]["methods"]):
            method_name += "_call"
        fields, values = parameters(
            "native", method["params"][0]["schema"], parent + pascal(method_name), {"profile"}
        )
        # Open native parameter schemas keep a lossless extension path.
        fields.append("extra_params: Mapping[str, Any] | None = None")
        result = qualified(
            "native", type_of("native", method["result"]["schema"], parent + "Result")
        )
        classes[parent].extend(
            [
                f"    async def {method_name}(self, *, {', '.join(fields)}) -> {result}:",
                f"        {method.get('summary', method['name'])!r}",
                f"        params = _payload({dict_code(values)}, extra_params)",
                "        if 'profile' in params:",
                "            raise TypeError('Profile is bound by the resource; select another profile resource')",
                f"        return typing.cast({result!r}, await self._native({method['name']!r}, params))",
                "",
            ]
        )
        native_coverage[method["name"]] = f"{parent}Resource.{method_name}"

    for cls, children in CHILDREN.items():
        for attr, child in children.items():
            classes[cls].extend(
                [
                    "    @property",
                    f"    def {attr}(self) -> {child}Resource:",
                    f"        return {child}Resource(self._sdk, **self._scope)",
                    "",
                ]
            )
    for cls, (child, key) in COLLECTIONS.items():
        key_type = "int" if key == "account_index" else "str"
        scope_value = f"str({key})" if key_type == "int" else key
        classes[cls].extend(
            [
                f"    def __call__(self, {key}: {key_type}) -> {child}Resource:",
                f"        if {key} <= 0:" if key_type == "int" else f"        if not {key}:",
                "            raise ValueError('Resource ID must not be empty')",
                f"        return {child}Resource(self._sdk, **{{**self._scope, {key!r}: {scope_value}}})",
                "",
            ]
        )
    for cls, op, field, terminal in [
        ("Job", "getProvisioningJob", "phase", ["ready", "failed", "cancelled"]),
        ("Build", "getImageBuild", "status", ["succeeded", "failed", "cancelled"]),
        ("Turn", "getTurn", "status", ["completed", "failed", "stopped", "waiting_for_approval"]),
    ]:
        result_type = {
            "Job": "_types_control_plane.ProvisioningJob",
            "Build": "_types_images.ImageBuild",
            "Turn": "_types_runtime.Turn",
        }[cls]
        classes[cls].extend(
            [
                f"    async def wait(self, *, timeout: float = 300, poll_interval: float = 0.5) -> {result_type}:",
                f"        return typing.cast({result_type!r}, await self._wait({op!r}, {field!r}, set({terminal!r}), timeout=timeout, poll_interval=poll_interval))",
                "",
            ]
        )
    classes["Turn"].extend(
        [
            "    async def stop(self) -> Any:",
            "        return await self.action(body={'type': 'stop'})",
            "",
            "    async def steer(self, content: str) -> Any:",
            "        return await self.action(body={'type': 'steer', 'content': content})",
            "",
            "    async def approve(self, request_id: str, decision: Literal['allow_once', 'allow_session', 'deny']) -> Any:",
            "        return await self.action(body={'type': 'approval', 'requestId': request_id, 'decision': decision})",
            "",
        ]
    )
    classes["Profile"].extend(
        [
            "    def connect(self) -> AbstractAsyncContextManager[NativeConnection]:",
            "        return connect(self._sdk, instance_id=self._scope['instance_id'], profile_id=self._scope['profile_id'])",
            "",
        ]
    )
    classes["Provider"].extend(
        [
            "    async def login(self, *, open_browser: bool = False, idempotency_key: str | Unset = UNSET) -> ProviderLoginResource:",
            "        return typing.cast('ProviderLoginResource', await self._login(open_browser=open_browser, idempotency_key=idempotency_key))",
            "",
        ]
    )
    header = '''"""Generated typed convenience resources. Do not edit; run scripts/generate_sdk.py."""
from __future__ import annotations
import builtins
import typing
from collections.abc import AsyncIterator, Mapping
from contextlib import AbstractAsyncContextManager
from typing import Any, Literal, Union
from ..duplex import NativeConnection, connect
from ..resources import Resource, UNSET, Unset, payload as _payload
from ..provider_auth import ProviderResourceBase, ProviderLoginBase
'''
    header += "\n".join(f"from . import types_{ns} as _types_{ns}" for ns in docs) + "\n\n"
    bases = {"Provider": "ProviderResourceBase", "ProviderLogin": "ProviderLoginBase"}
    content = header + "\n".join(
        f"class {name}Resource({bases.get(name, 'Resource')}):\n" + "\n".join(lines) + "\n"
        for name, lines in sorted(classes.items())
    )
    (output / "resources.py").write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")
    for ns, definitions in models.items():
        header = '"""Generated wire-shape types; required keys are explicit. Do not edit."""\n'
        header += "from __future__ import annotations\nimport builtins\nfrom typing import Any, Literal, Union\nfrom typing_extensions import Required, TypedDict, TypeAlias\n"
        header += (
            "\n".join(f"from . import types_{other}" for other in docs if other != ns) + "\n\n"
        )
        ordered = sorted(definitions.values(), key=lambda s: ": TypeAlias" in s)
        (output / f"types_{ns}.py").write_text(
            header + "\n".join(ordered), encoding="utf-8", newline="\n"
        )
    (output / "coverage.py").write_text(
        '"""Generated convenience API coverage manifest."""\n'
        + f"HTTP_COVERAGE = {coverage!r}\nNATIVE_COVERAGE = {native_coverage!r}\n",
        encoding="utf-8",
        newline="\n",
    )
