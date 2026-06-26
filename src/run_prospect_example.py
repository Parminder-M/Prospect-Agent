from datetime import date
from .agent_client import run_task

def main():
    prompt = (
        "Research Sage Group plc as a potential corporate funder. "
        "Check their CSR/foundation pages and any STEM education grants. "
        "Return a single Airtable-ready JSON record following the PRD schema."
    )

    result = run_task(prompt)

    print("[FINAL RESULT JSON]")
    print(result)

    # Later, you will transform `result` into Airtable rows and call upsert_records(...)
    # For now, we just print to see the shape.

if __name__ == "__main__":
    main()