import os
import requests
from typing import Dict, Any


AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")


def _get_airtable_url() -> str:
    """Return the base URL for the Airtable table."""
    if not AIRTABLE_BASE_ID or not AIRTABLE_TABLE_NAME:
        raise RuntimeError("Missing Airtable config: BASE_ID or TABLE_NAME")
    return f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"


def create_prospect_record(prospect: Dict[str, Any]) -> str:
    """
    Create a prospect record in Airtable.

    `prospect` should be a dict of field names to values, e.g.
    {
        "Company": "Acme Corp",
        "Segment": "STEM",
        "Score": 0.82,
    }

    Returns the Airtable record ID.
    """
    url = _get_airtable_url()
    if not AIRTABLE_API_KEY:
        raise RuntimeError("Missing AIRTABLE_API_KEY")

    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"fields": prospect}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["id"]


def update_prospect_record(record_id: str, fields: Dict[str, Any]) -> None:
    """
    Update an existing prospect record by ID.

    `fields` is a dict of field names to updated values.
    """
    url = f"{_get_airtable_url()}/{record_id}"
    if not AIRTABLE_API_KEY:
        raise RuntimeError("Missing AIRTABLE_API_KEY")

    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"fields": fields}
    response = requests.patch(url, headers=headers, json=payload)
    response.raise_for_status()