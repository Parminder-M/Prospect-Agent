“Claude Agent SDK test script in src/test_sdk.py demonstrates streaming messages; auth still to be configured.”


## Claude Agent SDK Integration

This project uses the Claude Agent SDK from Python to prototype a prospecting agent.

- Test script: `src/test_sdk.py`
- Current behavior: script connects to the SDK and streams messages, but returns an authentication error (`Not logged in · Please run /login`) until credentials are configured.

To configure authentication, set one of:

- `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token` using the Claude CLI), or
- `ANTHROPIC_API_KEY` (from the Anthropic Console),

in your `.env` file (see `.env.example`).

