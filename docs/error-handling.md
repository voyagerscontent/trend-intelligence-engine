# Error Handling

## Classification
- **Recoverable source error** — one source raises: caught per-source, logged as an
  `ingest` error, `source_errors` incremented, pipeline continues (`pipeline.ingest`).
- **Retryable HTTP** — connection errors and 429/500/502/503/504 on delivery: retried
  with bounded exponential backoff (`obs.request_with_retries`, `RetryPolicy`).
- **Terminal HTTP** — 4xx: raised immediately, never retried.
- **Terminal run failure** — anything uncaught: logged as `fatal`, a Slack alert is
  sent (`deliver/slack.py:alert_failure`, falls back to a printed alert if Slack is
  unconfigured), then re-raised so the process exits non-zero and CI shows red.

## Guarantees
- Every external call has a timeout (`RetryPolicy.timeout`, default 30s).
- Retries are **bounded** (`max_attempts`, default 3) — never unbounded against a
  rate-limited/paid API (red-flag blocker #6 addressed).
- No silent data loss: a failed run alerts and exits non-zero (red-flag blocker #4
  addressed for terminal failures). #retry-policy is in `obs.RetryPolicy`.

## Not yet covered (tracked)
- A durable dead-letter store for individual failed deliveries (P1-2). Today a terminal
  delivery failure fails the whole run loudly rather than dead-lettering one record.
