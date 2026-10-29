<p align="center"><img src="assets/branding/hermes-python-adk.svg" alt="Hermes Python ADK" width="100%"></p>

# Hermes SDK for Python

[![Python 3.10–3.14](https://img.shields.io/badge/Python-3.10--3.14-b68bff)](pyproject.toml)
[![Typed API](https://img.shields.io/badge/API-typed-f078c6)](docs/convenience-api.md)
[![Source version 0.35.0](https://img.shields.io/badge/source-0.35.0-e69acc)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![CI](https://github.com/AnasMaar/edith-hermes-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/AnasMaar/edith-hermes-sdk/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-8a6bd1)](https://anasmaar.github.io/edith-hermes-sdk/)

Build applications that provision and control Hermes runtimes, or connect to an existing Hermes deployment. The SDK provides typed control-plane resources, native RPC access, and separate bindings for Hermes Desktop HTTP routes.

[Documentation](https://anasmaar.github.io/edith-hermes-sdk/) · [Getting started](docs/getting-started/installation.md) · [Runtimes](docs/guides/runtimes.md) · [Native chat](docs/guides/native-chat.md) · [Examples](examples/README.md) · [Source](https://github.com/AnasMaar/edith-hermes-sdk)

## Install

Python 3.10–3.14 is supported. Until a registry release is available, install from a checkout:

```bash
git clone https://github.com/AnasMaar/edith-hermes-sdk.git
cd edith-hermes-sdk
python -m pip install .
python -m pip install ".[control-plane]"  # Local control plane
python -m pip install ".[streaming]"      # Remote WebSocket and event streaming
```

## Quickstart: a tool without a server

This example validates and invokes a Python tool locally. It requires no Docker, credentials, Hermes server, or model:

```python
import asyncio
from edith_hermes import Agent, tool

@tool
def word_count(text: str) -> int:
    """Count whitespace-separated words."""
    return len(text.split())

async def main() -> None:
    agent = Agent("Example", tools=[word_count])
    print(agent.tools[0].definition())
    print(await agent.tools[0].invoke({"text": "hello Hermes"}))  # 2

asyncio.run(main())
```

Run the complete version with `python examples/local_tool.py`. To send a prompt to a configured runtime, follow [first chat](docs/getting-started/first-chat.md). To provision a new runtime, see [runtimes](docs/guides/runtimes.md).

## Choose a client

| Need | Entry point | Backend |
| --- | --- | --- |
| Provision runtimes and agents; use resource handles | `Hermes.local()` / `Hermes.remote()` | EDITH control plane |
| Use generated HTTP operations directly | `AsyncEdithHermes.remote()` / `.local()` | EDITH control plane |
| Receive native events and answer server requests | `profile.connect()` | Control-plane gateway WebSocket and compatible native runtime |
| Work with native Desktop schedules, files, Git and skills | `AsyncHermesDesktop.remote()` | Hermes Desktop HTTP server |

A native Desktop URL is not a control-plane URL. Connecting to an existing Hermes installation through the control plane requires a registered instance and profile. A generated method reflects the pinned contract, not a guarantee that a particular server supports it. See [transport selection](docs/getting-started/installation.md).

## Documentation

- [First chat and approvals](docs/getting-started/first-chat.md)
- [Runtimes, Python tools, profiles and models](docs/guides/runtimes.md)
- [Existing native sessions, events and approvals](docs/guides/native-chat.md)
- [Desktop, connectors, plugins, schedules and workspaces](docs/guides/desktop.md)
- [Architecture](docs/guides/architecture.md), [authentication](docs/guides/authentication.md), and [reliability](docs/guides/reliability.md)
- [Control-plane configuration](docs/configuration.md), [provider authentication](docs/provider-auth.md), and [WebSocket protocol](contracts/websocket/gateway.md)
- [Convenience API coverage](docs/convenience-api.md) and [Desktop API](docs/desktop-api.md)

## Development

Install the development dependencies in `pyproject.toml`, then run `python -m pytest`. Live runtime tests require their own services and credentials; client installation alone does not provide a model or Hermes server.

## License

The SDK is licensed under the [MIT License](LICENSE). The vendored Hermes Agent contract is accompanied by the [upstream MIT license](src/edith_hermes/licenses/LICENSE.hermes-agent.txt); see [contract sources](contracts/vendor/README.md) for provenance.
