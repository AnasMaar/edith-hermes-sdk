"""Define and exercise a typed Agent tool locally, without a runtime or model."""

import asyncio
import json

from edith_hermes import Agent, tool


@tool
def word_count(text: str) -> int:
    """Count whitespace-separated words."""
    return len(text.split())


async def main():
    agent = Agent("Example", tools=[word_count])
    print(
        json.dumps(
            {
                "tool": agent.tools[0].definition(),
                "result": await agent.tools[0].invoke({"text": "hello Hermes"}),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
