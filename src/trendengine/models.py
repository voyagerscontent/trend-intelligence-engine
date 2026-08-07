"""Core data contracts shared across every stage.

These three dataclasses are the *only* objects that move between stages:

    Signal  --(cluster)-->  Trend  --(brief)-->  Brief

Keeping the contract narrow is what lets each stage be built, tested and
swapped independently. The auditor checks that every source returns Signal
objects and that Trend carries exactly the factor keys the scorer expects.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Signal:
    """One normalised observation from a single source."""
    source: str            # module NAME, e.g. "ahrefs_search"
    entity: str            # keyword / prompt / topic / competitor
    brand: str             # which property it maps to (see config/brands.yaml)
    value: float           # volume, mentions, sightings, audience size...
    change_pct: float      # momentum vs the prior period (e.g. 0.35 = +35%)
    captured_at: str       # ISO timestamp
    meta: dict[str, Any] = field(default_factory=dict)  # raw context for the brief

    def key(self) -> str:
        return f"{self.source}:{self.brand}:{self.entity.lower().strip()}"


@dataclass
class Trend:
    """A cluster of corroborating signals, scored and ranked."""
    title: str
    brand: str
    signals: list[Signal] = field(default_factory=list)
    factors: dict[str, float] = field(default_factory=dict)  # per-factor 0..1
    score: float = 0.0        # final 0..100
    rationale: str = ""
    brief: "Brief | None" = None

    @property
    def source_count(self) -> int:
        return len({s.source for s in self.signals})


@dataclass
class Brief:
    """The deliverable: a multichannel content brief for one trend."""
    title: str
    brand: str
    angle: str = ""
    audience: str = ""
    intent_stage: str = ""
    hero_format: str = ""
    keyword: str = ""
    ai_prompt: str = ""          # the GEO/AEO target
    bait_mechanic: str = ""
    channels: dict[str, str] = field(default_factory=dict)
    visual_notes: str = ""
    cta: str = ""
    owner: str = ""
    due: str = ""
    kpi: str = ""
    body_markdown: str = ""      # rendered brief

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
