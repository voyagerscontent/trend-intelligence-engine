# Deployment & Rollback

## Environments
- **CI / dry-run:** `audit.yml` runs static audit + tests + a no-credential dry-run on
  every push. This is the gate.
- **Scheduled prod:** `daily-ingest.yml` (06:00 UTC) and `weekly-briefs.yml` (Mon 06:00
  UTC) run with real secrets from GitHub Actions `secrets.*`.
- Keep separate Airtable base IDs / Slack channels for staging vs prod via the
  respective secret values. [confirm staging base exists before P1]

## Release
Follow `audits/<date>-trend-intelligence-engine/` scorecard + the release checklist.
Deploy = merge to the default branch (workflows pick up the new version). Bump `VERSION`
+ `__version__` + `pyproject.toml` together.

## Rollback
- Code: revert the merge / re-deploy the previous tag; workflows immediately run the
  prior version. Engine is stateless between runs, so rollback is a code revert only.
- Data: Airtable upserts are idempotent and non-destructive (no deletes), so a bad run
  updates rows rather than losing them; correct by re-running the previous version.
- Dry-run the rollback once before first prod deploy and record it here. [confirm]
