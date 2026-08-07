# Observability

## Structured logs
Every run emits JSON-lines to stdout (captured by GitHub Actions), each carrying a
`run_id` correlation ID (`obs.log_event`). Events: `start, ingest, score, http, done,
fatal`. You can answer "what happened to run X" by filtering one `run_id`, e.g.:

```
python -m trendengine.pipeline --dry-run | jq 'select(.run_id=="<id>")'
```

Sample line:
`{"run_id":"5046b7edf09e","event":"done","level":"info","signals":11,"trends":8,"escalated":3,"briefed":3,"source_errors":0}`

## Alerting
- Terminal failure → Slack alert via `alert_failure` (or printed if Slack unconfigured).
- **To wire before P1 live:** alert on `source_errors > threshold`, on a zero-signal
  run, and on failure-rate over N runs. Today only terminal crashes alert. [confirm]

## What to watch
- `done.briefed` should be ≥1 on weekly runs; a sustained 0 means the gates or sources
  regressed.
- `ingest.error` lines by source; a source erroring every run needs its adapter fixed.
- Retry `http` warn lines climbing = a provider is degraded/rate-limiting.
