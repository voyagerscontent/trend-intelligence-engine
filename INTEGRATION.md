# Integrating with the Trend Intelligence Engine

This repo is built to be consumed by the org's other repos (the Voyagers,
GalapagosIslands.travel and Polar Cruises sites, plus any internal tooling).
There are three supported interop surfaces — pick the one that fits.

All secrets live in **this** repo's Actions secrets. Consuming repos trigger a
run; they never receive the credentials.

---

## 1. Install it as a Python package

The engine is a standard `src`-layout package (`trendengine`), so any repo or
environment can install it straight from GitHub — no publish step needed:

```bash
pip install "git+https://github.com/voyagerscontent/trend-intelligence-engine.git@main"
```

Pin to a release tag for reproducible builds:

```bash
pip install "git+https://github.com/voyagerscontent/trend-intelligence-engine.git@v0.1.0"
```

Then use it directly:

```python
from trendengine.pipeline import run_pipeline

result = run_pipeline(stage="briefs", dry_run=True)
print(result.signals, result.trends, result.briefed)
```

Or via the console script:

```bash
trendengine --stage briefs --dry-run
```

---

## 2. Call the reusable GitHub Actions workflow

Another repo can run the whole pipeline from its own workflow with `uses:`.
Point at `.github/workflows/reusable-briefs.yml` and pass the secrets:

```yaml
# in a consuming repo, e.g. voyagers-website/.github/workflows/refresh-briefs.yml
name: refresh-briefs
on:
  schedule:
    - cron: "0 7 * * 1"
  workflow_dispatch: {}

jobs:
  briefs:
    uses: voyagerscontent/trend-intelligence-engine/.github/workflows/reusable-briefs.yml@main
    with:
      stage: briefs
      dry_run: false
    secrets: inherit      # forwards the caller org's secrets to the engine
```

`secrets: inherit` passes the calling repo's org-level secrets through. If you
keep the keys only in the engine repo instead, run method 3.

---

## 3. Trigger a run with `repository_dispatch`

Any external service, script, or another repo holding a PAT with `repo` scope
can kick off a run by POSTing an event — useful for "regenerate briefs now"
buttons, CMS webhooks, or cross-repo automation:

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  https://api.github.com/repos/voyagerscontent/trend-intelligence-engine/dispatches \
  -d '{"event_type":"run-briefs","client_payload":{"stage":"briefs","dry_run":false}}'
```

`client_payload.stage` (`ingest` | `briefs` | `all`) and `client_payload.dry_run`
(bool) are honored by the reusable workflow.

---

## What comes back

Regardless of trigger, delivery is idempotent:

- **Airtable** — the board is upserted on `Title` + `Brand` (safe to re-run).
- **Slack** — a shortlist is posted only on briefing runs (`briefs` / `all`),
  never on the daily ingest.

See `AUDIT.md` for the architecture contract and `docs/` for the full spec.
