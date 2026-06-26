print("Loaded test_sdk.py")

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    print("Starting SDK test...")
    async for message in query(
        prompt="Say hello.",
        options=ClaudeAgentOptions(allowed_tools=[]),
    ):
        print("Received message:", message)


if __name__ == "__main__":
    asyncio.run(main())
