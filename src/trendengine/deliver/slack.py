"""Push the ranked shortlist to Slack for one-click human approval.

Dry-run (no SLACK_TOKEN) prints the message instead of posting.
"""
from __future__ import annotations

from ..models import Trend
from ..obs import RetryPolicy, redact, request_with_retries
from ..settings import Settings

_API = "https://slack.com/api/chat.postMessage"


def _format(trends: list[Trend]) -> str:
    lines = ["*Weekly trend shortlist* — approve to brief:"]
    for i, t in enumerate(trends, 1):
        lines.append(f"{i}. *{t.score}* · [{t.brand}] {t.title} — {t.rationale}")
    return "\n".join(lines)


def deliver_slack(trends: list[Trend], settings: Settings, dry_run: bool = False,
                  run_id: str = "-") -> str:
    text = _format(trends)
    if dry_run or not (settings.slack_token and settings.slack_channel):
        print("[slack dry-run] would post:\n" + text)
        return text
    request_with_retries(
        "POST", _API, policy=RetryPolicy(), run_id=run_id,
        headers={"Authorization": f"Bearer {settings.slack_token}"},
        json={"channel": settings.slack_channel, "text": text},
    )
    return text


def alert_failure(settings: Settings, run_id: str, summary: str, dry_run: bool = False) -> str:
    """Post a failure alert to Slack so failures are never silent (blocker #4).

    Falls back to a printed alert line when Slack isn't configured, so the
    failure is always surfaced somewhere the operator can see it.
    """
    text = redact(f":rotating_light: trend-engine run {run_id} FAILED — {summary}")
    if dry_run or not (settings.slack_token and settings.slack_channel):
        print("[alert] " + text)
        return text
    try:
        request_with_retries(
            "POST", _API, policy=RetryPolicy(), run_id=run_id,
            headers={"Authorization": f"Bearer {settings.slack_token}"},
            json={"channel": settings.slack_channel, "text": text},
        )
    except Exception:  # alerting must never mask the original failure
        print("[alert] " + text)
    return text
