async def main():
    print("Starting SDK test...")
    try:
        async for message in query(
            prompt="Say hello.",
            options=ClaudeAgentOptions(allowed_tools=[]),
        ):
            print("Received message:", message)
    except Exception as e:
        print("\nSDK raised an exception:")
        print(e)
        print(
            "\nHint: If you see 'Not logged in · Please run /login', "
            "set CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY in your .env."
        )