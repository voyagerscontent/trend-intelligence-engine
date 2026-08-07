# Naming & Versioning

## Versioning
- Package version lives in `pyproject.toml` and `src/trendengine/__init__.py`
  (`__version__`), and in the `VERSION` file. Bump together (SemVer).
- Cross-stage contracts (`Signal`, `Trend`, `Brief` in `models.py`) are versioned by
  the package version; a breaking change to any field is a MAJOR bump and must update
  `docs/data-contracts.md` and `schemas/*.schema.json` in the same change.
- Scoring model (`score.FACTORS` + `config/weights.yaml`) changes are MINOR unless a
  factor is removed/renamed (MAJOR). `scripts/audit_static.py` blocks config/code drift.

## Naming
- Sources: `snake_case` module + a unique `NAME` constant; registered in
  `sources/__init__.py:REGISTRY`.
- Env vars: `UPPER_SNAKE`, documented in `.env.example` (enforced by the static audit).
- Structured log events: lower-case `event` names (start, ingest, score, http, done,
  fatal).
