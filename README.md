# Trend Intelligence Engine

Turns market signals into multimedia, multichannel **content briefs** for
high-touch South America & Polar expedition travel — the production engine
behind Voyagers, GalapagosIslands.travel and Polar Cruises & Tours.

Five stages, run on a schedule, land finished briefs in your team's lap:

```
LISTEN  →  CLUSTER  →  SCORE  →  BRIEF  →  DELIVER
sources    cluster     score     brief     Slack + Airtable
```

It runs **end-to-end with zero credentials** in dry-run mode (each source
emits sample signals), so you can see a real brief before wiring a single API.

## Quickstart

```bash
pip install -e ".[dev]"
cp .env.example .env                       # fill in keys as you get them
python -m trendengine.pipeline --dry-run   # full loop, prints a brief
```

Expected tail: `DONE · signals=… trends=… escalated=… briefed=…`.

## Layout

| Path | Role |
|------|------|
| `src/trendengine/sources/` | one module per signal source (Ahrefs, GSC, Trends, social, news) |
| `src/trendengine/models.py` | the only cross-stage contracts: `Signal`, `Trend`, `Brief` |
| `src/trendengine/cluster.py` · `score.py` | grouping + the weighted scoring model |
| `src/trendengine/brief/` | Claude-drafted brief + Jinja template |
| `src/trendengine/deliver/` | Airtable board + Slack shortlist |
| `src/trendengine/config/` | `weights.yaml`, `brands.yaml`, voice profile — tune without code |
| `.github/workflows/` | `daily-ingest`, `weekly-briefs`, and the `audit` gate |

## Tuning

- **Re-target brands/topics/competitors:** edit `config/brands.yaml`.
- **Re-tune the score:** edit `config/weights.yaml` (keys are checked against code).
- **Add a source:** create `sources/<name>.py` with a `NAME` + `fetch()`, add it
  to `REGISTRY`, add its key to `.env.example`. The auditor verifies the rest.

## Use from other repos

This engine is built to be driven by the org's other repos. Three ways in —
`pip install` it as a package, call its reusable GitHub Actions workflow with
`uses:`, or fire a `repository_dispatch` event. Secrets stay in this repo; a
caller only triggers a run. Full recipes in **[INTEGRATION.md](INTEGRATION.md)**.

## Auditing (start clean, stay clean)

This repo ships with its own auditor so glitches are caught up front:

```bash
python scripts/audit_static.py     # deterministic invariants (see AUDIT.md)
pytest -q                          # unit tests
```

Both run automatically on every push via `.github/workflows/audit.yml`. There's
also a project-specific review agent at `.claude/agents/trend-engine-auditor.md`
— in Claude Code, ask it to audit before merging any change. See `AUDIT.md` for
the architecture map and the full list of enforced invariants.

## Status

Scaffold / walking skeleton. Source modules return **sample** data until their
API key is set; each has a `TODO(live)` marking exactly where to wire the real
call. The contract, scoring, briefing and delivery paths are complete and tested.
