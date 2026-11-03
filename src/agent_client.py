"""Runs the prospecting agent via the Claude Agent SDK."""
import asyncio
import json
import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Union

from claude_agent_sdk import ClaudeAgentOptions, query

from .config import require_claude_auth

# Optional, private list of the Nonprofit's current partners (one name per line).
# Kept out of git: see .gitignore and data/existing_partners.example.txt.
PARTNERS_FILE = Path(os.getenv("PROSPECT_PARTNERS_FILE", "data/existing_partners.txt"))

SYSTEM_PROMPT = """
You are a prospecting agent for a STEM youth nonprofit ("the Nonprofit").
The Nonprofit funds STEM/youth outreach via corporates, foundations and HNWIs.

Research
- Prefer primary sources: the prospect's own annual report, foundation or CSR pages,
  the Charity Commission register, 360Giving GrantNav. Use news or aggregator sites
  only when no primary source exists, and say so.
- Note the date of the evidence. Treat anything older than 3 years as weak.

Exclusions (check first)
- EXCLUDE sectors: defence, gambling, tobacco (including a material division in one).
- EXCLUDE existing partners of the Nonprofit, using the partner list provided.
  If no list is provided, do not exclude on this basis; add "Check partner list" to to_verify.
- For an excluded prospect: priority_tier "Excluded", total_score 0, and say why in why_them.

Scoring (each 0-2)
- Capacity: can they give at a meaningful level?
- Programmatic fit: do they fund STEM, youth or education now?
- Strategic relevance: is there a live route in (an open grant scheme, a foundation
  that takes applications, a named contact or programme that partners with charities)?

Priority tier (use exactly one of these values)
- "A": total 5-6 AND strategic relevance is 2 (a live funding route was found)
- "B": total 4-6 otherwise
- "C": total 0-3
- "Excluded": hit an exclusion rule

Output: return ONLY one JSON object, no other text, with exactly these fields:
- entity_id: "<type>-<name-slug>", type is corp, fdn or hnwi (e.g. "corp-sage-group")
- entity_type: "Corporate", "Foundation" or "Individual"
- name, country
- priority_tier: one of the tier values above
- total_score: integer 0-6
- capacity, programmatic_fit, strategic_relevance: integers 0-2
- status_change: "New", "Updated" or "Excluded"
- why_them: 2-5 sentences; every claim backed by a link in source_links
- to_verify: list of short items a volunteer must check before outreach
- source_links: list of URLs, primary sources first
- last_refreshed_date: today's date, YYYY-MM-DD

Never guess the Nonprofit's real name. Always call it "the Nonprofit".
""".strip()

RESEARCH_TOOLS = ["WebSearch", "WebFetch"]

# Cost controls, overridable in .env:
# - a mid-tier model is plenty for "read pages, score against a rubric"
# - a hard spend cap per prospect stops a runaway research loop
MODEL = os.getenv("PROSPECT_MODEL", "sonnet")
MAX_BUDGET_USD = float(os.getenv("PROSPECT_MAX_BUDGET_USD", "0.50"))

TIERS = {"A", "B", "C", "Excluded"}
STATUSES = {"New", "Updated", "Excluded"}
REQUIRED = [
    "entity_id", "entity_type", "name", "country", "priority_tier", "total_score",
    "capacity", "programmatic_fit", "strategic_relevance", "status_change",
    "why_them", "to_verify", "source_links", "last_refreshed_date",
]


def _partner_context() -> str:
    if PARTNERS_FILE.exists():
        names = [n.strip() for n in PARTNERS_FILE.read_text().splitlines() if n.strip()]
        if names:
            return "\n\nExisting partners of the Nonprofit (exclude these): " + "; ".join(names)
    return "\n\nNo partner list was provided."


async def _run_query(user_prompt: str) -> Dict[str, Any]:
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT + f"\n\nToday's date: {date.today().isoformat()}" + _partner_context(),
        model=MODEL,
        tools=RESEARCH_TOOLS,          # load only the research tools (cuts prompt overhead)
        allowed_tools=RESEARCH_TOOLS,  # and auto-approve them: no file or shell access
        setting_sources=[],            # ignore any local Claude Code settings or CLAUDE.md
        max_turns=15,
        max_budget_usd=MAX_BUDGET_USD,
    )
    final = {"text": "", "cost_usd": None, "turns": None}
    async for message in query(prompt=user_prompt, options=options):
        result = getattr(message, "result", None)
        if result:
            final["text"] = result
        if getattr(message, "total_cost_usd", None) is not None:
            final["cost_usd"] = message.total_cost_usd
            final["turns"] = getattr(message, "num_turns", None)
    return final


def _parse_json(text: str) -> Union[Dict[str, Any], List[Any], str]:
    """Parse the agent's answer as JSON, tolerating a ```json fence or extra text."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                pass
        return text


def validate_record(record: Any) -> List[str]:
    """Check a record against the schema and the scoring rules. Returns a list of problems."""
    if not isinstance(record, dict):
        return ["Output was not a JSON object"]
    problems = [f"Missing field: {f}" for f in REQUIRED if f not in record]
    tier, status = record.get("priority_tier"), record.get("status_change")
    if tier not in TIERS:
        problems.append(f"priority_tier {tier!r} is not one of {sorted(TIERS)}")
    if status not in STATUSES:
        problems.append(f"status_change {status!r} is not one of {sorted(STATUSES)}")
    parts = [record.get(k) for k in ("capacity", "programmatic_fit", "strategic_relevance")]
    total = record.get("total_score")
    if tier == "Excluded":
        if total != 0:
            problems.append("Excluded prospects must have total_score 0")
    elif all(isinstance(p, int) and 0 <= p <= 2 for p in parts):
        if total != sum(parts):
            problems.append(f"total_score {total} does not equal the sub-scores ({sum(parts)})")
        expected = "C" if total <= 3 else ("A" if total >= 5 and parts[2] == 2 else "B")
        if tier in TIERS and tier != expected:
            problems.append(f"priority_tier {tier} does not follow the tier rules (expected {expected})")
    else:
        problems.append("Sub-scores must be integers 0-2")
    if not record.get("source_links"):
        problems.append("No source_links")
    return problems


def research_prospect(user_prompt: str) -> Dict[str, Any]:
    """Research one prospect. Returns the record, any validation problems, cost and turns."""
    require_claude_auth()
    run = asyncio.run(_run_query(user_prompt))
    record = _parse_json(run["text"])
    return {
        "record": record,
        "problems": validate_record(record),
        "cost_usd": run["cost_usd"],
        "turns": run["turns"],
    }


def run_task(user_prompt: str) -> Union[Dict[str, Any], List[Any], str]:
    """Backwards-compatible entry point: returns just the record."""
    return research_prospect(user_prompt)["record"]
