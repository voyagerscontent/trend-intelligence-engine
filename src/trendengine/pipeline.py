"""Orchestrates the five stages: LISTEN -> CLUSTER -> SCORE -> BRIEF -> DELIVER.

Run it directly:
    python -m trendengine.pipeline --stage all --dry-run
or via the console script:
    trendengine --stage briefs
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass

from .config_loader import load_brands, load_weights
from .brief import generate_brief
from .cluster import cluster
from .deliver import alert_failure, deliver_airtable, deliver_slack
from .models import Signal, Trend
from .normalize import normalize
from .obs import log_event, new_run_id
from .score import rank, score_trend
from .settings import Settings, load_settings
from .sources import REGISTRY


@dataclass
class PipelineResult:
    signals: int
    trends: int
    escalated: list[Trend]
    briefed: int
    run_id: str = "-"
    source_errors: int = 0


def ingest(settings: Settings, brands: dict, run_id: str = "-") -> tuple[list[Signal], int]:
    signals: list[Signal] = []
    errors = 0
    for source in REGISTRY:
        try:
            got = source.fetch(settings, brands)
            log_event(run_id, "ingest", source=source.NAME, count=len(got))
            signals.extend(got)
        except Exception as exc:  # a broken source must never break the pipeline
            errors += 1
            log_event(run_id, "ingest", "error", source=source.NAME, error=repr(exc))
    return signals, errors


def run_pipeline(stage: str = "all", dry_run: bool = True) -> PipelineResult:
    settings = load_settings()
    run_id = new_run_id()
    log_event(run_id, "start", stage=stage, dry_run=dry_run)
    try:
        return _run(stage, dry_run, settings, run_id)
    except Exception as exc:  # terminal failure: alert, then re-raise so CI fails loudly
        log_event(run_id, "fatal", "error", error=repr(exc))
        alert_failure(settings, run_id, f"stage={stage}: {exc!r}", dry_run=dry_run)
        raise


def _run(stage: str, dry_run: bool, settings: Settings, run_id: str) -> PipelineResult:
    weights = load_weights()
    brands = load_brands()
    thresholds = weights["thresholds"]

    raw, source_errors = ingest(settings, brands, run_id)
    signals = normalize(raw)
    trends = [score_trend(t, weights, brands) for t in cluster(signals, brands)]

    # Two gates before a trend can be shortlisted or briefed:
    #  (1) corroboration — must appear across >= min_sources_to_escalate sources
    #  (2) brand fit (luxury gate) — off-brand trends never reach a brief
    escalated = rank([
        t for t in trends
        if t.source_count >= thresholds["min_sources_to_escalate"]
        and t.factors["brand_fit"] >= thresholds["min_brand_fit"]
    ])
    log_event(run_id, "score", trends=len(trends), escalated=len(escalated),
              min_sources=thresholds["min_sources_to_escalate"],
              min_brand_fit=thresholds["min_brand_fit"])

    if stage in ("briefs", "all"):
        for t in escalated:
            if t.score >= thresholds["min_score_to_brief"]:
                generate_brief(t, settings)

    briefed = [t for t in escalated if t.brief]

    # Airtable refreshes the board on every run (idempotent upsert).
    deliver_airtable(briefed or escalated, settings, dry_run=dry_run, run_id=run_id)
    # Slack shortlist is only for the briefing runs — not the daily ingest.
    if stage in ("briefs", "all"):
        deliver_slack(escalated, settings, dry_run=dry_run, run_id=run_id)

    log_event(run_id, "done", signals=len(signals), trends=len(trends),
              escalated=len(escalated), briefed=len(briefed), source_errors=source_errors)
    return PipelineResult(
        signals=len(signals),
        trends=len(trends),
        escalated=escalated,
        briefed=len(briefed),
        run_id=run_id,
        source_errors=source_errors,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Trend Intelligence Engine pipeline")
    parser.add_argument("--stage", choices=["ingest", "briefs", "all"], default="all")
    parser.add_argument("--dry-run", action="store_true",
                        help="Never call delivery APIs; print instead.")
    args = parser.parse_args(argv)
    result = run_pipeline(stage=args.stage, dry_run=args.dry_run)
    print(f"\nDONE · signals={result.signals} trends={result.trends} "
          f"escalated={len(result.escalated)} briefed={result.briefed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
