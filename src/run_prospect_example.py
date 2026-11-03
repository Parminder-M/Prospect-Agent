"""Research one or more prospects and print the scored records.

Usage:
    python -m src.run_prospect_example "Sage Group plc"
    python -m src.run_prospect_example "Sage Group plc" "Wellcome Trust" --save

--save writes each record to output/<entity_id>.json (output/ is not committed).
"""
import json
import sys
from pathlib import Path

from .agent_client import research_prospect


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    save = "--save" in sys.argv
    names = args or ["Sage Group plc"]
    total_cost = 0.0

    for name in names:
        prompt = (
            f"Research {name} as a potential funder. "
            "Check their annual report, foundation or CSR pages and any STEM or education grants. "
            "Return a single JSON record following the schema."
        )
        run = research_prospect(prompt)
        record = run["record"]
        print(json.dumps(record, indent=2, ensure_ascii=False) if not isinstance(record, str) else record)

        cost = run["cost_usd"] or 0.0
        total_cost += cost
        print(f"\n[{name}] cost ${cost:.3f} · {run['turns']} turns")
        if run["problems"]:
            print("[check] Fix before use: " + "; ".join(run["problems"]))
        else:
            print("[check] Record passes schema and tier rules")

        if save and isinstance(record, dict):
            out = Path("output") / f"{record.get('entity_id', name)}.json"
            out.parent.mkdir(exist_ok=True)
            out.write_text(json.dumps(record, indent=2, ensure_ascii=False))
            print(f"[saved] {out}")
        print()

    if len(names) > 1:
        print(f"Total cost for {len(names)} prospects: ${total_cost:.3f}")


if __name__ == "__main__":
    main()
