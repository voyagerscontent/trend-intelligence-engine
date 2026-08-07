# Test Plan

## Automated (run in CI on every push — `audit.yml`)
- `scripts/audit_static.py` — 7 architecture invariants (source contract, weights↔
  factors, env documented, no secrets, all stages + gates + alert + logging wired,
  modules parse, brands valid).
- `python -m pytest` — 10 unit tests:
  - `test_cluster.py` — destination token alone does not fake corroboration; a genuine
    shared intent corroborates across sources.
  - `test_score.py` — weights match FACTORS and sum to 1.0; score bounded 0–100;
    high-momentum corroborated trend clears the brief threshold.
  - `test_pipeline.py` — dry-run produces ≥1 brief; every escalated trend has ≥2 sources.
  - `test_models.py` — signal key stable/case-insensitive; source_count distinct.
  - `test_sources.py` — every source returns `Signal`s in dry-run; names unique.
- End-to-end dry-run — full loop with no credentials prints a brief and `done` line.

## Coverage vs the kit's required scenarios
- Happy path — covered (dry-run + pipeline test).
- Invalid input — partial: sources are stubs; add malformed-payload fixtures when a
  live adapter lands (P1).
- Partial failure — covered: `test`/design ensures one broken source doesn't stop the run.
- Rate-limit / timeout — retry logic unit-testable via `obs.request_with_retries`
  (inject `sleep`); add an explicit test when wiring a live HTTP source (P1).

## Before every deploy
Run: `python scripts/audit_static.py && python -m pytest && python -m trendengine.pipeline --dry-run`
and record the result/date in the release checklist.
