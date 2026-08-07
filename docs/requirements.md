# Requirements

Priorities: **P0** = required for go-live, **P1** = next, **P2** = later.
Acceptance criteria use Given/When/Then.

## P0 — required for go-live
- **P0-1 Corroboration gate.**
  Given signals for a brand, When a trend appears on fewer than
  `min_sources_to_escalate` distinct sources, Then it is not escalated or briefed.
  (Evidence: `tests/test_pipeline.py`, `pipeline.py`.)
- **P0-2 Brand-fit (luxury) gate.**
  Given a scored trend, When `brand_fit < min_brand_fit`, Then it is never
  shortlisted or briefed. (Evidence: `pipeline.py`, `score.py`.)
- **P0-3 Offline dry-run.**
  Given no credentials, When the pipeline runs `--dry-run`, Then it completes and
  emits ≥1 brief from sample signals. (Evidence: dry-run tail `briefed>=1`.)
- **P0-4 Idempotent delivery.**
  Given the same trend on repeated runs, When delivered to Airtable, Then rows are
  upserted on Title+Brand (no duplicates). (Evidence: `deliver/airtable.py`.)
- **P0-5 No silent failure.**
  Given a terminal error, When the run fails, Then a structured `fatal` log line and
  a Slack alert are emitted and the process exits non-zero. (Evidence: `pipeline.py`,
  `deliver/slack.py:alert_failure`.)
- **P0-6 Secret hygiene.**
  Given the repo, When scanned, Then no real secret literals exist; all env vars are
  documented in `.env.example`. (Evidence: `scripts/audit_static.py`.)

## P1
- P1-1 Wire one real source (Ahrefs) end-to-end against staging.
- P1-2 Persist an audit trail of runs (run_id, counts, outcome) beyond CI logs.
- P1-3 Alert on failure-rate / zero-signal runs, not just terminal crashes.

## P2
- P2-1 Claude-drafted briefs in the Stephen Sancho voice (scaffold present).
- P2-2 Historic trend store to measure momentum over real time windows.

## Non-Goals (explicit — not "N/A")
- The engine does **not** publish content anywhere; it delivers briefs for humans.
- It does **not** auto-approve or auto-send anything customer-facing.
- It does **not** store personal/PII data; sources are keyword/topic/aggregate only.
- It is **not** a CMS, analytics dashboard, or rank tracker replacement.
