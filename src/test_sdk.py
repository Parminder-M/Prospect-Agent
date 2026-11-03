"""Smoke test: checks the Claude Agent SDK is installed and authenticated.

Usage:
    python -m src.test_sdk
"""
import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query

from .config import require_claude_auth


async def main() -> None:
    require_claude_auth()
    print("Starting SDK test...")
    async for message in query(prompt="Say hello.", options=ClaudeAgentOptions(allowed_tools=[])):
        print("Received message:", message)


if __name__ == "__main__":
    asyncio.run(main())
