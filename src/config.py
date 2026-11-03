"""Configuration loaded from environment variables (see .env.example).

The Claude Agent SDK reads ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN from the
environment itself, so we only check that one of them is present.
"""
import os

from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Prospects")


def require_claude_auth() -> None:
    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_CODE_OAUTH_TOKEN")):
        raise RuntimeError(
            "Set ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN in .env (see .env.example)."
        )
