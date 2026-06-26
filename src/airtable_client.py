from pyairtable import Table
from .config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME

def get_table():
    return Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)

def upsert_records(records: list[dict]):
    """
    records: list of dicts with Airtable 'fields' payload.
    If you already have ids, use update; otherwise create.
    """
    table = get_table()
    for rec in records:
        rec_id = rec.get("id")
        fields = rec["fields"]
        if rec_id:
            table.update(rec_id, fields)
        else:
            table.create(fields)