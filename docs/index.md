---
title: Hermes SDK for Python
description: Start with a Python tool, connect a running Hermes instance, and build your own agent application.
hide:
  - toc
---

<div class="sdk-hero" markdown>

<span class="sdk-kicker">Hermes SDK / Python</span>

# Your application.<br>Your Hermes runtime.

<p class="sdk-lead">Connect the agent you already run, or provision a new one. Build conversations, Python tools and profile-aware integrations through an asynchronous, typed API.</p>

<div class="sdk-actions" markdown>

[Get started](getting-started/installation.md){ .md-button .md-button--primary }
[Explore the cookbook](cookbook/index.md){ .md-button }

</div>

<p class="sdk-meta">Python 3.10–3.14 · Source version 0.35.0 · No Docker requirement for client-only use</p>

</div>

## Start where you are

<div class="sdk-paths" markdown>

<div class="sdk-path" markdown>
<span class="sdk-label">01 / Connect</span>

### I already run Hermes

Use a registered runtime through the control plane, or connect directly to Hermes Desktop's HTTP API for supported operations.

[Choose the correct client →](guides/architecture.md)
</div>

<div class="sdk-path" markdown>
<span class="sdk-label">02 / Build</span>

### I want Python tools and agents

Define a typed function, attach it to an agent, and choose a process, container, external or Kubernetes runtime.

[Build your first conversation →](getting-started/first-chat.md)
</div>

<div class="sdk-path" markdown>
<span class="sdk-label">03 / Integrate</span>

### I am building an application

Start with practical recipes for native events, approvals, schedules, bots, groups and plugin discovery.

[Find a working example →](cookbook/index.md)
</div>

</div>

## Try the tool boundary in a minute

This runs entirely in Python. It creates no runtime, sends no model request and needs no credentials.
Install the SDK from a checkout using the [installation guide](getting-started/installation.md).

<p class="sdk-code-label">A typed tool, without infrastructure</p>

~~~python
import asyncio
from edith_hermes import tool


@tool
def shipping_cost(weight_kg: float, rate_per_kg: float = 4.5) -> dict[str, float]:
    """Calculate a shipping quote."""
    return {"cost": round(weight_kg * rate_per_kg, 2)}


async def main() -> None:
    print(shipping_cost.definition()["name"])
    print(await shipping_cost.invoke({"weight_kg": 2}))


asyncio.run(main())
~~~

Expected output:

~~~text
shipping_cost
{'cost': 9.0}
~~~

The same tool can be attached to an [agent](guides/runtimes.md). The callable's annotations
define its input schema; invalid arguments are rejected before its body runs.

## Pick the right boundary

| What you need | Start here | Service required |
| --- | --- | --- |
| Provision instances and manage agent conversations | [Hermes and resource handles](reference/agents.md) | EDITH control plane, in-process or deployed |
| Call typed generated HTTP operations | [AsyncEdithHermes](reference/clients.md) | EDITH control plane |
| Native chat events and interactive requests | [Native sessions](guides/native-chat.md) | Registered runtime and compatible gateway/bridge |
| Schedules, files, Git, Skills Hub and the plugin catalog | [AsyncHermesDesktop](reference/desktop.md) | Native Hermes Desktop HTTP server |
| Checked mutations and application extensions | [Versioned extensions](extensions.md) | Matching advertised backend extension |

These endpoints are different. A model-provider URL, a native Desktop URL and a control-plane
URL cannot be substituted for each other.

## Build the workflow you need

- **A chat client:** persist the owning instance, profile and session IDs; consume native events and handle approvals. [Chat recipe](cookbook/chat-and-events.md)
- **A scheduled assistant:** inspect jobs, create a paused schedule explicitly and reconcile uncertain mutations. [Schedules recipe](cookbook/schedules.md)
- **A bot integration:** keep the profile and group/session ownership explicit when delivering messages or attachments. [Bots and groups](cookbook/bot-groups.md)
- **A plugin-aware application:** discover the actual deployment's catalog and connector support before offering actions. [Integrations recipe](cookbook/integrations.md)

## Know what has been verified

The documentation embeds the example source files; the API pages are generated from the
SDK's exported classes. Offline fixtures exercise request routing, sessions and WebSocket
frames. They do not establish that your provider, OAuth account or running Hermes version
supports an operation.

See [compatibility](compatibility.md), [authentication](guides/authentication.md) and
[verification](release/verification.md) before deploying an application.

This is an independent project built around [Nous Research's Hermes Agent](https://github.com/NousResearch/hermes-agent).
Installing the client does not install a Hermes runtime or supply model access.
