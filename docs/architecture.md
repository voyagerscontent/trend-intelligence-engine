# Architecture

Five single-responsibility stages, orchestrated by `pipeline.run_pipeline`:

```
LISTEN   sources/*.fetch()      -> list[Signal]   (+ normalize.normalize dedupe)
CLUSTER  cluster.cluster()      -> list[Trend]    (discriminating-token grouping)
SCORE    score.score_trend/rank -> list[Trend]    (weighted model + two gates)
BRIEF    brief.generate_brief   -> Brief          (deterministic; Claude-upgraded if keyed)
DELIVER  deliver.deliver_airtable / deliver_slack (idempotent board + shortlist)
```

Diagrams: `architecture/system-flow.mmd`, `architecture/error-flow.mmd`.

## Single-responsibility units
- `sources/` — one module per signal source, each behind the `SignalSource` contract
  (`sources/base.py`): unique `NAME`, `fetch()` returns `[]` on error and sample data
  when unkeyed. Discovery is via `REGISTRY`.
- `normalize.py` — dedupe identical observations.
- `cluster.py` — group by discriminating tokens (brand namesake / theme terms excluded
  so corroboration counts are real, not faked on the destination name).
- `score.py` — transparent weighted model; `FACTORS` is the single source of truth,
  matched to `config/weights.yaml` by `scripts/audit_static.py`.
- `brief/` — deterministic brief + Jinja template; optional Claude upgrade.
- `deliver/` — Airtable (idempotent upsert) + Slack (shortlist + failure alerts).
- `obs.py` — structured logging (run_id correlation) + bounded-retry HTTP helper.

## Contracts across stages
Only `Signal`, `Trend`, `Brief` (`models.py`) cross stage boundaries — see
`docs/data-contracts.md`. Nothing else is passed between stages.

## Orchestration & scheduling
`pipeline.run_pipeline(stage, dry_run)`; scheduled by three GitHub Actions workflows
(`daily-ingest`, `weekly-briefs`, `audit`). The map and its invariants are enforced by
`AUDIT.md` + `scripts/audit_static.py` and reviewed by
`.claude/agents/trend-engine-auditor.md`.
