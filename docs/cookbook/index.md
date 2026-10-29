# Cookbook

These recipes use the SDK against an existing deployment, except the local tool example. Install `python -m pip install "edith-hermes-sdk[streaming]"` for the WebSocket recipes. From a checkout, use `python -m pip install -e ".[streaming]"`. Download the linked Python files or run their commands from the checkout root. Python 3.10–3.14 is supported.

Use a dedicated sandbox profile and ask your deployment administrator for the control-plane HTTP URL, instance ID, profile ID, and access token if needed. Set `EDITH_TOKEN` in your shell; do not put tokens in command arguments. Replace uppercase placeholders below with actual values. A control-plane profile ID can differ from its native profile name; the connector and schedule recipes resolve the name. The Desktop recipe instead uses the direct Desktop URL, native profile name, and optional `HERMES_DESKTOP_TOKEN`.

- [Chat and events](chat-and-events.md): inspect sessions, stream a prompt, and review approvals.
- [Tools](tools.md): define and invoke a typed local tool.
- [Schedules](schedules.md): list schedules and create a paused job.
- [Integrations](integrations.md): discover plugins, connectors, groups, and agents.
- [Bots and groups](bot-groups.md): send a bot message or group attachment.

All live writes require `--run`. Prompt, bot, and group operations can invoke a model and incur charges. Check your deployment supports the relevant native methods and extensions; the SDK does not supply a model, runtime, credentials, or an external service. The scripts print JSON that can include sensitive information.

For offline checks, install development dependencies and run `python -m pytest tests/test_documented_examples.py`. Those tests use isolated HTTP and WebSocket protocol fixtures and do not establish support on a live deployment. See the [examples README](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/examples/README.md) for all commands and cleanup notes.
