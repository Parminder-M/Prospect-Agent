# Prospect Agent

An AI research agent that helps a small STEM youth charity find and prioritise new funders. Give it a company, foundation or person; it researches them on the web, applies the charity's exclusion rules, scores fit on a fixed rubric and returns a sourced record ready for the charity's prospect tracker in Airtable.

Built as a volunteer project for a charity I've supported for 10 years. The charity is referred to as "the Nonprofit" throughout.

**Status:** working prototype. Piloted on three real prospects in November 2026: about **$0.05 per prospect** and a minute or two each, with every record passing its own schema check. Sample outputs are in [`examples/`](examples/), before and after the fixes.

## The problem

The Nonprofit relies on corporate, foundation and high-net-worth donors, but has no one with time for funder research. Prospecting meant volunteers reading CSR pages and annual reports by hand, so research was slow, inconsistent between volunteers and rarely revisited.
<!-- TODO (Parminder): add a real number if you have one, e.g. "a volunteer spent about X hours per prospect" -->

## What it does

For each prospect, the agent:

1. **Researches** from primary sources first: the prospect's annual report, foundation or CSR pages, the Charity Commission register and 360Giving GrantNav.
2. **Applies exclusions:** defence, gambling and tobacco (including a material division in one), and anyone already on the Nonprofit's partner list.
3. **Scores** three criteria, 0–2 each:
   - **Capacity:** can they give at a meaningful level?
   - **Programmatic fit:** do they fund STEM, youth or education now?
   - **Strategic relevance:** is there a live route in, such as an open grant scheme?
4. **Assigns a tier** by fixed rules: **A** = 5–6 *and* a live funding route; **B** = 4–6 otherwise; **C** = 0–3; **Excluded**.
5. **Returns** one JSON record with a short "why them", a source for every claim, and a `to_verify` list for the volunteer.
6. **Checks its own output** against the schema and tier rules, and flags anything that breaks them.

## Pilot results (November 2026)

The same three prospects, run before and after tightening the rules:

| Prospect | First run | After fixes | Why it changed |
|---|---|---|---|
| Sage Group plc | "Tier 1", 5/6 | **B**, 4/6 | No open funding route found, so it can't be A-tier |
| Rolls-Royce Holdings | "Excluded", but scored 5/6 | **Excluded**, 0/6 | Defence is about 24% of revenue; the agent now checks exclusions first and stops (2 turns, $0.02) |
| Wellcome Trust | B, 4/6 | **C**, 3/6 | Found that the only public-engagement scheme is closed and only for Wellcome-funded researchers; suggests an indirect route instead |

After the fixes, all three records passed the validator. The second round cost **$0.14 for three prospects** on Sonnet, with a hard cap of $0.50 each. Outputs: [`examples/v1-first-runs`](examples/v1-first-runs/) and [`examples/v2-after-fixes`](examples/v2-after-fixes/).

## What I learned from the first runs

Reading the first outputs as a reviewer found five problems; four are fixed:

1. **Confident priority on thin evidence.** Sage was rated "Tier 1" although the agent found no open funding route. **Fix:** tiers follow fixed thresholds, and A-tier needs a live route.
2. **Format drift.** The three runs used three tier formats ("Tier 1", "B", "Excluded"), and an excluded prospect still scored 5. **Fix:** strict allowed values, plus a validator that checks every record. It flagged all three first runs.
3. **Weak sources.** Financial figures came from stock-market aggregators rather than the company's own report. **Fix:** a primary-sources-first rule, with evidence older than three years treated as weak.
4. **A rule it couldn't follow.** "Exclude existing partners" was impossible without the partner list. **Fix:** an optional, private partner list passed in as input; without it, the agent adds "check partner list" to `to_verify` instead of guessing.

5. **Run-to-run variance.** Sage's programmatic fit dropped from 2 to 1 between runs, because the second run didn't find the 2022 programme the first one did. Same prospect, different evidence, different score. **Not fixed yet:** this is why the next step is an eval set that runs each prospect several times and measures how stable the tiers are.

The general lesson: the model was good at research and consistent at scoring, but loose at overall judgement and formatting. Explicit rules plus an automatic check did more than a longer prompt.

## Design decisions

- **A rubric, not a ranking.** Fixed 0–2 scores make results comparable across runs and easy for a volunteer to challenge.
- **Sources or it didn't happen.** Every claim needs a link, so a human can check it before anyone makes contact.
- **A human makes the call.** The agent shortlists; volunteers decide who to approach.
- **Research, not contact details.** Contact discovery stays with a human using an enrichment tool (such as Apollo or Lusha) on shortlisted prospects only. That respects LinkedIn's terms, keeps data protection decisions with the charity, and saves paid credits.
- **Least privilege.** The agent can only search and read the web: no file or shell access.
- **Cost controls.** Sonnet by default, only the two research tools loaded, and a per-prospect spend cap.
- **Anonymised by default.** The agent never uses the charity's real name, and the partner list is never committed.

## What it changed
<!-- TODO (Parminder): the most important line for readers. What has the charity done, or will it do, with this? E.g. "Used to build a first shortlist of N prospects for the 2027 corporate campaign" or "Handed to the fundraising volunteer to pilot on the next 20 prospects". -->

## What's next

- Batch runs from a list, writing straight to Airtable (the client is written in `src/airtable_client.py`).
- A small eval set: about 10 prospects with tiers agreed by a volunteer, each run three times, to measure agreement and stability.
- A scheduled monthly refresh, so A- and B-tier prospects stay current.

## Run it

Requires Python 3.10+.

```bash
pip install -r requirements.txt
cp .env.example .env        # add ANTHROPIC_API_KEY (or CLAUDE_CODE_OAUTH_TOKEN)
python -m src.test_sdk      # smoke test: checks auth
python -m src.run_prospect_example "Sage Group plc"
python -m src.run_prospect_example "Sage Group plc" "Wellcome Trust" --save   # several, saved to output/
```

Optional: copy `data/existing_partners.example.txt` to `data/existing_partners.txt` and list the Nonprofit's partners. That file is never committed. Model and spend cap can be changed in `.env`.
