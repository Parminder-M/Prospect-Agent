import asyncio
from datetime import date
from typing import Any, Dict

from claude_agent_sdk import query, ClaudeAgentOptions
from .config import ANTHROPIC_API_KEY, CLAUDE_PROJECT_ID  # CLAUDE_PROJECT_ID not used here now

SYSTEM_PROMPT = """
You are a prospecting agent for a STEM youth nonprofit ("the Nonprofit").
The Nonprofit funds STEM/youth outreach via corporates and HNWIs.

Rules:
- EXCLUDE sectors: defence, gambling, tobacco.
- EXCLUDE existing partners listed in the annual reports.
- Score each prospect: Capacity (0-2) + Programmatic Fit (0-2) + Strategic Relevance (0-2).
- Output Airtable-ready JSON with fields: entity_id, entity_type, name, country,
  priority_tier, total_score, status_change, why_them, source_links, last_refreshed_date.
- Never guess the Nonprofit's real name. Always call it "the Nonprofit".
""".strip()


async def _run_query(user_prompt: str) -> Dict[str, Any]:
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        allowed_tools=["WebSearch", "WebFetch"],
        permission_mode="acceptEdits",
        max_turns=20,
    )

    final_result: Dict[str, Any] = {}

    async for message in query(prompt=user_prompt, options=options):
        if hasattr(message, "result") and message.result is not None:
            final_result = message.result

    return final_result


def run_task(user_prompt: str) -> Dict[str, Any]:
    """
    Synchronous wrapper that you can call from your scripts.
    """
    return asyncio.run(_run_query(user_prompt))