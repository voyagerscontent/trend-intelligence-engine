# Operations Runbook

## Owner / on-call
- **Owner:** Marcel (marcel@latintrails.com). [confirm — this names the responsible
  human required by red-flag blocker #7; replace/extend with on-call if the team grows.]

## What this system does
Pulls market signals daily, clusters + scores them, and delivers escalated,
on-brand trends as multichannel briefs to Airtable (board) and Slack (approval
shortlist) for Voyagers / GalapagosIslands.travel / Polar Cruises & Tours.

## Daily health check (under 2 minutes)
1. Open the latest `daily-ingest` / `weekly-briefs` Actions run.
2. Confirm the final `done` log line has `briefed>=1` (weekly) and `source_errors` low.
3. Skim for `ingest error` lines — a source erroring every run needs its adapter fixed.

## Common issues
- **No briefs produced:** check the two gates (`min_sources_to_escalate`,
  `min_brand_fit`) and that sources returned signals (`ingest` counts).
- **A source errors every run:** its credential or API changed — fix the adapter; the
  pipeline keeps running on the others by design.
- **Delivery failing:** look for `http` warn/retry lines and the `fatal` alert; verify
  Airtable/Slack tokens in GitHub secrets.

## Recovery
Runs are stateless and idempotent — safe to re-run a failed schedule manually via
"Run workflow" in Actions. No manual data cleanup needed (Airtable upserts).

## Escalation
If a run fails and the alert fires, the owner triages within the day; nothing here is
customer-facing or spends money, so blast radius is internal content operations.
