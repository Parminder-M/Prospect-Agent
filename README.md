# Prospect Agent

An AI research agent that helps a small STEM youth charity find and prioritise new funders. Given a company or person, it researches them on the web, screens out poor fits and returns a scored, sourced record ready to drop into the charity's prospect tracker in Airtable.

Built as a volunteer project for a charity I've supported for 10 years. The charity is referred to as "the Nonprofit" throughout.

## The problem

The Nonprofit relies on corporate and high-net-worth donors, but nobody has time for funder research. Prospecting meant volunteers reading CSR pages and annual reports by hand, so good prospects were missed and the pipeline was inconsistent.
<!-- TODO (Parminder): add a real number if you have one, e.g. "about X hours per prospect" -->

## What it does

For each prospect, the agent:

1. **Researches** the organisation or person: CSR and foundation pages, STEM or education grants, annual reports.
2. **Screens** against the charity's rules: excludes defence, gambling and tobacco, and anyone who is already a partner.
3. **Scores** fit on three criteria, 0–2 each (maximum 6):
   - **Capacity:** can they give at a meaningful level?
   - **Programmatic fit:** do they fund STEM, youth or education?
   - **Strategic relevance:** is there a link to the charity's work, region or network?
4. **Returns** one JSON record with a priority tier, a short "why them" and source links for every claim, in the schema the charity's Airtable base uses.

```json
{
  "entity_id": "...",
  "entity_type": "corporate",
  "name": "Example Group plc",
  "country": "UK",
  "priority_tier": "A",
  "total_score": 5,
  "status_change": "new",
  "why_them": "Runs a STEM education fund for 11–18s in the UK ...",
  "source_links": ["https://..."],
  "last_refreshed_date": "2026-11-03"
}
```

## How it works

```
prospect name ──► Claude Agent SDK ──► WebSearch / WebFetch ──► rules + scoring ──► JSON record ──► (Airtable)
```

- **Claude Agent SDK** (Python) runs the research loop, up to 20 turns.
- The agent can **only search and read the web**: no file or shell access.
- **The rules sit in the system prompt** (`src/agent_client.py`), so the charity's criteria can be changed without touching code.
- **Airtable client** (`src/airtable_client.py`) creates and updates records. It is written but not yet wired into the main run.

## Design decisions

- **A scoring rubric, not a ranking.** Fixed 0–2 scores on three criteria make results comparable across runs and easy for a volunteer to challenge.
- **Sources or it didn't happen.** Every "why them" claim needs a link, so a human can check it before anyone makes contact.
- **Anonymised by default.** The agent never uses the charity's real name, so research prompts can't leak it.
- **A human makes the call.** The agent prioritises; volunteers decide who to approach.

## What it changed
<!-- TODO (Parminder): the most important section for readers. Examples:
     - how many prospects researched, how many new A-tier prospects found
     - time per prospect before vs after
     - what the charity did with the list
     If it's still early, say so plainly: "Piloted on N prospects; ..." -->

## What I learned / what's next
<!-- TODO (Parminder): an honest line or two. Possible candidates:
     - first version tried to do everything in one prompt; splitting rules into a rubric made results consistent
     - next: batch runs from a list, write straight to Airtable, a simple eval set to check scoring accuracy -->

## Run it

Requires Python 3.10+.

```bash
pip install -r requirements.txt
cp .env.example .env        # add ANTHROPIC_API_KEY (or CLAUDE_CODE_OAUTH_TOKEN)
python -m src.test_sdk      # smoke test: checks auth
python -m src.run_prospect_example "Sage Group plc"
```

Airtable settings in `.env` are only needed once results are written to a base.
