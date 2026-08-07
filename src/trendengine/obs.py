"""Observability: structured logging + a bounded-retry HTTP helper.

Every pipeline run gets a `run_id` (a correlation ID) that is stamped on every
structured log line, so any job is traceable end-to-end without reading the raw
GitHub Actions console. `log_event` emits one JSON object per line (JSON-lines),
which downstream tooling (or `jq`) can filter by `run_id`, `stage`, or `level`.

`request_with_retries` gives every external call a timeout, a bounded number of
attempts, and exponential backoff — so a rate-limited or flaky API is retried a
fixed number of times and then fails loudly, never silently and never forever.
See docs/observability.md and docs/error-handling.md.
"""
from __future__ import annotations

import json
import re
import sys
import time
import uuid
from dataclasses import dataclass, field

# Never let a credential reach a log line, an exception repr, or an alert.
# Matches Airtable PATs, Slack tokens, Anthropic keys, and any "Bearer <x>".
_SECRET_RE = re.compile(
    r"(pat[A-Za-z0-9]{10,}\.[A-Za-z0-9]{16,})"
    r"|(xox[baprs]-[A-Za-z0-9-]{10,})"
    r"|(sk-ant-[A-Za-z0-9\-]{10,})"
    r"|(key[A-Za-z0-9]{14,})"
    r"|(Bearer\s+\S+)"
)


def redact(text: str) -> str:
    """Scrub anything that looks like a token out of a string."""
    return _SECRET_RE.sub("[REDACTED]", text)


def new_run_id() -> str:
    """A short correlation ID for one pipeline run."""
    return uuid.uuid4().hex[:12]


def log_event(run_id: str, event: str, level: str = "info", **fields) -> None:
    """Emit one structured JSON log line to stdout (captured by CI).

    `event` is the pipeline phase/name (start, ingest, score, http, done, ...);
    extra keyword fields are merged in (e.g. stage=, source=, count=).

    The serialized line is redacted before printing so a token can never leak
    into logs, even via an exception repr (e.g. requests' InvalidHeader).
    """
    record = {"run_id": run_id, "event": event, "level": level}
    record.update(fields)
    print(redact(json.dumps(record, default=str)), file=sys.stdout, flush=True)


@dataclass
class RetryPolicy:
    """Bounded retry with exponential backoff. Never unbounded (blocker #6)."""
    max_attempts: int = 3
    base_delay: float = 0.5     # seconds; doubles each attempt
    timeout: float = 30.0       # per-request timeout, seconds

    # Only these transport/HTTP conditions are retried; a 4xx is terminal.
    retry_statuses: frozenset = field(default_factory=lambda: frozenset({429, 500, 502, 503, 504}))


def request_with_retries(method: str, url: str, policy: RetryPolicy | None = None,
                         run_id: str = "-", sleep=time.sleep, **kwargs):
    """requests.request wrapped in timeout + bounded exponential backoff.

    Retries only on connection errors and retryable status codes (429/5xx).
    A 4xx (bad request) is terminal and raised immediately — we never retry a
    request the server has already rejected. Raises the last error after
    `max_attempts` so failures are loud, not silent.
    """
    import requests  # imported lazily so offline/dry-run paths never need it

    pol = policy or RetryPolicy()
    kwargs.setdefault("timeout", pol.timeout)
    last_exc: Exception | None = None

    for attempt in range(1, pol.max_attempts + 1):
        try:
            resp = requests.request(method, url, **kwargs)
            if resp.status_code in pol.retry_statuses and attempt < pol.max_attempts:
                delay = pol.base_delay * (2 ** (attempt - 1))
                log_event(run_id, "http", "warn", url=url, status=resp.status_code,
                          attempt=attempt, retry_in=delay)
                sleep(delay)
                continue
            resp.raise_for_status()
            return resp
        except requests.HTTPError as exc:  # non-retryable (4xx) -> terminal
            status = getattr(exc.response, "status_code", None)
            if status in pol.retry_statuses and attempt < pol.max_attempts:
                last_exc = exc
                delay = pol.base_delay * (2 ** (attempt - 1))
                log_event(run_id, "http", "warn", url=url, status=status,
                          attempt=attempt, retry_in=delay)
                sleep(delay)
                continue
            raise
        except requests.RequestException as exc:  # connection/timeout -> retry
            last_exc = exc
            if attempt < pol.max_attempts:
                delay = pol.base_delay * (2 ** (attempt - 1))
                log_event(run_id, "http", "warn", url=url, error=type(exc).__name__,
                          attempt=attempt, retry_in=delay)
                sleep(delay)
                continue
            raise
    if last_exc:
        raise last_exc
