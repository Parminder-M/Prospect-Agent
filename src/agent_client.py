"""Runs the prospecting agent via the Claude Agent SDK."""
import asyncio
import os
import json
from typing import Any, Dict, List, Union

from claude_agent_sdk import ClaudeAgentOptions, query

from .config import require_claude_auth

SYSTEM_PROMPT = """
You are a prospecting agent for a STEM youth nonprofit ("the Nonprofit").
The Nonprofit funds STEM/youth outreach via corporates and HNWIs.

Rules:
- EXCLUDE sectors: defence, gambling, tobacco.
- EXCLUDE existing partners listed in the annual reports.
- Score each prospect: Capacity (0-2) + Programmatic Fit (0-2) + Strategic Relevance (0-2).
- Output Airtable-ready JSON with fields: entity_id, entity_type, name, country,
  priority_tier, total_score, status_change, why_them, source_links, last_refreshed_date.
- Every claim in why_them must be backed by a link in source_links.
- Never guess the Nonprofit's real name. Always call it "the Nonprofit".
- Return only the JSON, with no extra text.
""".strip()


RESEARCH_TOOLS = ["WebSearch", "WebFetch"]

# Cost controls, overridable in .env:
# - a mid-tier model is plenty for "read pages, score against a rubric"
# - a hard spend cap per prospect stops a runaway research loop
MODEL = os.getenv("PROSPECT_MODEL", "sonnet")
MAX_BUDGET_USD = float(os.getenv("PROSPECT_MAX_BUDGET_USD", "0.50"))


async def _run_query(user_prompt: str) -> str:
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        model=MODEL,
        tools=RESEARCH_TOOLS,          # load only the research tools (cuts prompt overhead)
        allowed_tools=RESEARCH_TOOLS,  # and auto-approve them: no file or shell access
        setting_sources=[],            # ignore any local Claude Code settings or CLAUDE.md
        max_turns=15,
        max_budget_usd=MAX_BUDGET_USD,
    )
    final_text = ""
    async for message in query(prompt=user_prompt, options=options):
        result = getattr(message, "result", None)
        if result:
            final_text = result
    return final_text


def _parse_json(text: str) -> Union[Dict[str, Any], List[Any], str]:
    """Parse the agent's answer as JSON, tolerating a ```json fence. Falls back to raw text."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return text


def run_task(user_prompt: str) -> Union[Dict[str, Any], List[Any], str]:
    """Synchronous entry point: research a prospect and return the scored record."""
    require_claude_auth()
    return _parse_json(asyncio.run(_run_query(user_prompt)))
