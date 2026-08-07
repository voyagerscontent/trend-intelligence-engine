"""Score and rank trends with a transparent, tunable weighted model.

FACTORS is the single source of truth for the scoring dimensions. The keys
under `weights:` in config/weights.yaml MUST match FACTORS exactly and sum
to 1.0 — scripts/audit_static.py enforces both invariants so config and code
can never silently drift.
"""
from __future__ import annotations

import math

from .models import Trend

FACTORS = [
    "demand",
    "momentum",
    "brand_fit",
    "competitive_gap",
    "monetisability",
    "freshness",
]

_HIGH_INTENT = {"operator", "cruise", "trip", "book", "price", "cost", "tour", "package"}


def _demand(trend: Trend) -> float:
    peak = max((s.value for s in trend.signals), default=0.0)
    return min(1.0, math.log10(peak + 1) / 5.0)  # 100k+ audience -> 1.0


def _momentum(trend: Trend) -> float:
    peak = max((s.change_pct for s in trend.signals), default=0.0)
    return max(0.0, min(1.0, peak))  # +100% change -> 1.0


def _brand_fit(trend: Trend, brands: dict) -> float:
    cfg = (brands.get("brands") or {}).get(trend.brand, {})
    seed = " ".join(cfg.get("seed_topics", []))
    seed_tokens = set(seed.lower().split())
    title_tokens = set(trend.title.lower().split())
    return 0.85 if seed_tokens & title_tokens else 0.55


def _competitive_gap(trend: Trend) -> float:
    if any(s.meta.get("citation_gap") for s in trend.signals):
        return 0.9
    if any(s.meta.get("competitor") for s in trend.signals):
        return 0.7
    return 0.5


def _monetisability(trend: Trend) -> float:
    title_tokens = set(trend.title.lower().split())
    return 0.75 if title_tokens & _HIGH_INTENT else 0.4


def _freshness(trend: Trend) -> float:
    # All sample signals are same-day; a real decay would use captured_at age.
    return 1.0


def compute_factors(trend: Trend, brands: dict) -> dict[str, float]:
    return {
        "demand": _demand(trend),
        "momentum": _momentum(trend),
        "brand_fit": _brand_fit(trend, brands),
        "competitive_gap": _competitive_gap(trend),
        "monetisability": _monetisability(trend),
        "freshness": _freshness(trend),
    }


def score_trend(trend: Trend, weights: dict, brands: dict) -> Trend:
    w = weights["weights"]
    factors = compute_factors(trend, brands)
    trend.factors = factors
    trend.score = round(sum(w[f] * factors[f] for f in FACTORS) * 100, 1)
    top = sorted(factors.items(), key=lambda kv: kv[1], reverse=True)[:2]
    trend.rationale = (
        f"{trend.source_count} sources; driven by "
        + ", ".join(f"{k} {v:.2f}" for k, v in top)
    )
    return trend


def rank(trends: list[Trend]) -> list[Trend]:
    return sorted(trends, key=lambda t: t.score, reverse=True)
