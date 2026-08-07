"""Upsert trends + briefs to Airtable (the team-facing board).

Dry-run (no AIRTABLE_TOKEN) prints what would be written and returns the
records, so the pipeline is exercised end-to-end without credentials.
"""
from __future__ import annotations

import json

from ..models import Trend
from ..obs import RetryPolicy, request_with_retries
from ..settings import Settings

_API = "https://api.airtable.com/v0"
_TABLE = "Trends"


def _records(trends: list[Trend]) -> list[dict]:
    rows = []
    for t in trends:
        rows.append(
            {
                "fields": {
                    "Title": t.title,
                    "Brand": t.brand,
                    "Score": t.score,
                    "Sources": t.source_count,
                    "Rationale": t.rationale,
                    "Brief": t.brief.body_markdown if t.brief else "",
                }
            }
        )
    return rows


def deliver_airtable(trends: list[Trend], settings: Settings, dry_run: bool = False,
                     run_id: str = "-") -> list[dict]:
    rows = _records(trends)
    if dry_run or not (settings.airtable_token and settings.airtable_base_id):
        print(f"[airtable dry-run] would upsert {len(rows)} record(s):")
        print(json.dumps(rows, indent=2)[:1500])
        return rows
    url = f"{_API}/{settings.airtable_base_id}/{_TABLE}"
    headers = {
        "Authorization": f"Bearer {settings.airtable_token}",
        "Content-Type": "application/json",
    }
    # Idempotent upsert: merge on Title+Brand so re-runs update rows instead of
    # piling up duplicates (daily + weekly schedules both touch the board).
    # Every request has a timeout + bounded exponential backoff (see obs.py).
    for i in range(0, len(rows), 10):  # Airtable caps at 10 records/request
        payload = {
            "performUpsert": {"fieldsToMergeOn": ["Title", "Brand"]},
            "records": rows[i : i + 10],
        }
        request_with_retries("PATCH", url, policy=RetryPolicy(), run_id=run_id,
                             headers=headers, json=payload)
    return rows
