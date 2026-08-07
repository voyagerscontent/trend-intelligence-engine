# Data Contracts

## Cross-stage objects (the only ones that move between stages)
`Signal -> Trend -> Brief`, defined in `src/trendengine/models.py` and mirrored as
JSON Schema (draft 2020-12) in `schemas/signal.schema.json`,
`schemas/trend.schema.json`, `schemas/brief.schema.json`. Versioned by package version
(see `docs/naming-and-versioning.md`); a field change bumps the schema in the same
change.

`Trend.factors` keys are enforced to equal `score.FACTORS` by
`scripts/audit_static.py` (`weights_match_factors`), so scorer and contract cannot
drift.

## Data lineage
External source → `Signal` (per-source `fetch`) → dedupe (`normalize`) → `Trend`
(`cluster`) → scored `Trend` (`score`) → `Brief` (`brief`) → Airtable row / Slack
message (`deliver`). Correlation via `run_id` on every structured log line.

## Sensitive data / PII
- The engine handles **keywords, topics, aggregate metrics, and competitor domains**
  only. No names, emails, phone numbers, or other PII flow through any stage.
  (Evidence: PII marker scan returns none; see the audit evidence folder.)
- If a future live source (e.g. GSC anonymised queries, social listening) could surface
  personal data in a query string, it MUST be minimised at the source adapter before a
  `Signal` is created, and this section updated.
- Retention: sample runs hold no data; live runs write only derived trend/brief rows to
  Airtable. Set an Airtable retention/cleanup policy before P1 live wiring. [confirm]

## Idempotency
Airtable delivery upserts on `Title`+`Brand` (`deliver/airtable.py`), so repeated daily
+ weekly runs update rows instead of duplicating them.
