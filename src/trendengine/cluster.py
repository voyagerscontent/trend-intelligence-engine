"""Cluster signals into candidate trends.

Deterministic fallback (default): within a brand, group signals that share a
*discriminating* token. A token is non-discriminating when it is the brand's
namesake OR it appears in most of that brand's signals (the destination theme,
e.g. "antarctica", not the trend). Excluding those stops every signal collapsing
into one mega-cluster on the destination name — which would fake the
corroboration count — while still letting real shared intents (e.g. "cruise")
group together. Runs offline and is fully testable. When ANTHROPIC_API_KEY is
set, cluster_with_claude() can replace the semantic step — same contract.
"""
from __future__ import annotations

import math
import re

from .models import Signal, Trend

# Generic filler removed from every entity before matching.
_STOP = {"the", "to", "in", "of", "for", "a", "an", "and", "best", "time", "see", "is", "new"}

# A token appearing in >= this fraction of a brand's signals is the brand's
# theme, not a distinguishing trend, so it can't be used to corroborate. Set
# high (near-ubiquitous) so genuine sub-intents like "cruise" are preserved;
# known destination words are declared explicitly via brands.yaml:theme_terms.
_THEME_FRACTION = 0.8


def _tokens(entity: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", entity.lower())
    return {w for w in words if w not in _STOP and len(w) > 2}


def _declared_generic(brand_key: str, brands: dict) -> set[str]:
    """Brand name tokens + declared theme_terms — always non-discriminating."""
    cfg = (brands.get("brands") or {}).get(brand_key, {})
    words = set(re.findall(r"[a-z0-9]+", brand_key.lower()))
    words |= set(re.findall(r"[a-z0-9]+", str(cfg.get("name", "")).lower()))
    for term in cfg.get("theme_terms", []):
        words |= set(re.findall(r"[a-z0-9]+", str(term).lower()))
    return {w for w in words if len(w) > 2}


def _theme_tokens(signals: list[Signal]) -> set[str]:
    """Tokens shared by most of a brand's signals — the destination theme."""
    n = len(signals)
    if n < 3:
        return set()  # too few to infer a theme statistically
    freq: dict[str, int] = {}
    for s in signals:
        for tok in _tokens(s.entity):
            freq[tok] = freq.get(tok, 0) + 1
    cutoff = math.ceil(_THEME_FRACTION * n)
    return {tok for tok, c in freq.items() if c >= cutoff}


def cluster(signals: list[Signal], brands: dict) -> list[Trend]:
    by_brand: dict[str, list[Signal]] = {}
    for s in signals:
        by_brand.setdefault(s.brand, []).append(s)

    trends: list[Trend] = []
    for brand, group in by_brand.items():
        generic = _declared_generic(brand, brands) | _theme_tokens(group)

        clusters: list[list[Signal]] = []
        cluster_tokens: list[set[str]] = []
        for s in group:
            disc = _tokens(s.entity) - generic  # distinctive tokens only
            placed = False
            if disc:  # a signal with no distinctive token can't corroborate
                for i, ct in enumerate(cluster_tokens):
                    if disc & ct:
                        clusters[i].append(s)
                        cluster_tokens[i] |= disc
                        placed = True
                        break
            if not placed:
                clusters.append([s])
                cluster_tokens.append(set(disc))

        for members in clusters:
            title = max(members, key=lambda x: len(x.entity)).entity
            trends.append(Trend(title=title, brand=brand, signals=members))
    return trends
