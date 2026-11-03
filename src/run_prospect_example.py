"""Research one prospect and print the scored record.

Usage:
    python -m src.run_prospect_example "Sage Group plc"
"""
import json
import sys

from .agent_client import run_task


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "Sage Group plc"
    prompt = (
        f"Research {name} as a potential funder. "
        "Check their CSR/foundation pages and any STEM education grants. "
        "Return a single Airtable-ready JSON record following the schema."
    )
    result = run_task(prompt)
    print(json.dumps(result, indent=2) if not isinstance(result, str) else result)


if __name__ == "__main__":
    main()
