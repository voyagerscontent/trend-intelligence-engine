"""AI answer-engine visibility (GEO/AEO) from Ahrefs Brand Radar.

Tracks AI share-of-voice, mentions and the citation gap across ChatGPT,
Gemini and Perplexity. Dry-run returns sample signals.
"""
from __future__ import annotations

from datetime import datetime, timezone

from ..models import Signal
from ..settings import Settings

_NOW = lambda: datetime.now(timezone.utc).isoformat()


class AhrefsBrandRadarSource:
    NAME = "brandradar"

    def fetch(self, settings: Settings, brands: dict) -> list[Signal]:
        if not settings.ahrefs_api_key:
            return self._sample(brands)
        # TODO(live): call brand-radar sov-overview + mentions-overview +
        # cited-pages; a low SoV on a high-volume prompt is a citation-gap
        # opportunity -> Signal with meta['citation_gap']=True.
        return self._sample(brands)

    def _sample(self, brands: dict) -> list[Signal]:
        return [
            Signal(self.NAME, "which galapagos cruise is best for families", "galapagos",
                   1, 0.40, _NOW(), {"sov": 0.06, "citation_gap": True, "note": "sample"}),
            Signal(self.NAME, "best antarctica expedition operator", "voyagers",
                   1, 0.30, _NOW(), {"sov": 0.11, "citation_gap": True, "note": "sample"}),
        ]
