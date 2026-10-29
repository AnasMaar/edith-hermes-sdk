# Installation and transport selection

Install Python 3.10–3.14, then get a checkout:

~~~sh
git clone https://github.com/AnasMaar/edith-hermes-sdk.git
cd edith-hermes-sdk
python -m venv .venv
~~~

Activate the environment in your shell before installing:

=== "Bash"

    ~~~sh
    source .venv/bin/activate
    ~~~

=== "PowerShell"

    ~~~powershell
    .venv/Scripts/Activate.ps1
    ~~~

From the repository root, run:

```bash
python -m pip install .
python -m pip install ".[control-plane]"  # Local control plane and providers
python -m pip install ".[streaming]"      # Remote WebSocket and event streaming
```

These are checkout installs; they do not assume a package has been published. Extras can be combined: `python -m pip install ".[control-plane,streaming]"`.

## Select the endpoint

- **Local orchestration:** `Hermes.local(runtime=...)` starts an in-process control plane with SQLite and a Python tool listener. Provisioning a runtime still requires Docker, a Hermes executable, or an external endpoint, depending on your choice.
- **Remote orchestration:** `Hermes.remote(base_url, token=...)` connects to a running EDITH control plane. The control plane must enable the requested runtime provider. Closing this client does not delete remote instances.
- **Low-level operations:** `AsyncEdithHermes.remote(base_url=..., token=...)` targets the same control-plane HTTP API. `AsyncEdithHermes.local()` starts an in-process control plane; Docker must be enabled explicitly in its settings. `EdithHermes` offers synchronous remote/embedded operations.
- **Native gateway:** a control-plane profile's `connect()` provides a persistent WebSocket to the native Hermes gateway. Remote use requires the `streaming` extra and a compatible gateway/bridge.
- **Desktop REST:** `AsyncHermesDesktop.remote(base_url=..., profile=..., token=...)` targets the Hermes Desktop HTTP server directly, not the EDITH control plane.

Control-plane credentials, provider credentials and connector credentials are separate. Backend capabilities, authentication, runtime images and model availability are deployment-specific. The SDK does not install or authenticate a model for you.

Next: [first chat](first-chat.md), [runtime choices](../guides/runtimes.md), or [existing native sessions](../guides/native-chat.md).
