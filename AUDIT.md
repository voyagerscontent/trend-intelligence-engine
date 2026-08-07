# Architecture map & audited invariants

This file is the contract the project auditor enforces. If you change the
architecture, change this file **and** `scripts/audit_static.py` in the same
commit. The goal is to catch drift up front and avoid corrections later.

## The pipeline map

```
sources/*.fetch()          -> list[Signal]      (LISTEN)
normalize.normalize()      -> list[Signal]      (dedupe)
cluster.cluster()          -> list[Trend]       (CLUSTER)
score.score_trend()/rank() -> list[Trend]       (SCORE)
brief.generate_brief()     -> Brief             (BRIEF)
deliver.deliver_slack()    -> Slack shortlist   (DELIVER)
deliver.deliver_airtable() -> Airtable board    (DELIVER)
```
Orchestrated by `pipeline.run_pipeline(stage, dry_run)`; scheduled by the two
GitHub Actions workflows.

## Invariants (each maps to a check in audit_static.py)

| # | Invariant | Enforced by |
|---|-----------|-------------|
| 1 | Every source has a unique NAME + fetch(); all registered in REGISTRY | `source_contract` |
| 2 | `score.FACTORS` == `weights.yaml:weights` keys; weights sum to 1.0; all three thresholds present | `weights_match_factors` |
| 3 | Every env var used in code (incl. via `settings._get`) is documented in `.env.example` | `env_vars_documented` |
| 4 | No hardcoded secrets in code, config, or workflows | `no_hardcoded_secrets` |
| 5 | `pipeline.py` wires all five stages, **both gates** (corroboration + brand-fit), the **failure-alert** path, and **structured logging** | `pipeline_wires_all_stages` |
| 6 | All modules parse (no syntax errors) | `modules_parse` |
| 7 | Every brand in `brands.yaml` has name/role/seed_topics | `brands_config_valid` |

## Gates (both enforced in `pipeline.py`, wiring checked by invariant #5)

- **Corroboration:** a trend must appear across `>= min_sources_to_escalate`
  *distinct* sources — and clustering only corroborates on *discriminating*
  tokens (brand namesake / seed words are excluded) so the count is real.
- **Brand-fit (luxury gate):** `brand_fit >= min_brand_fit` before a trend is
  shortlisted or briefed. Off-brand spikes are logged, never briefed.

## Invariants the human/LLM auditor still owns (not statically checkable)

- Only `Signal` / `Trend` / `Brief` cross stage boundaries.
- Clustering does not over-merge distinct intents (inspect against dry-run).
- Sources degrade gracefully: sample signals when unkeyed, `[]` on error.
- Delivery is idempotent: Airtable upserts on Title+Brand; the Slack shortlist
  posts only on briefing runs (`briefs`/`all`), not the daily ingest.

## Runbook

```
pip install -e ".[dev]"
python scripts/audit_static.py            # invariants 1-7
pytest -q                                 # unit tests
python -m trendengine.pipeline --dry-run  # end-to-end, no credentials
```

## Planning, contracts & ops docs (added 2026-08-03)

Full standards set under `docs/` (problem-and-goals, requirements, architecture,
data-contracts, security-and-secrets, error-handling, observability,
deployment-and-rollback, operations-runbook, naming-and-versioning, test-plan),
JSON Schemas in `schemas/`, diagrams in `architecture/`, and the pre-production audit
in `audits/2026-08-03-trend-intelligence-engine/` (scorecard, decision record, findings,
evidence).
