"""Rising / seasonal interest from Google Trends (free corroboration)."""
from __future__ import annotations

from datetime import datetime, timezone

from ..models import Signal
from ..settings import Settings

_NOW = lambda: datetime.now(timezone.utc).isoformat()


class GoogleTrendsSource:
    NAME = "google_trends"

    def fetch(self, settings: Settings, brands: dict) -> list[Signal]:
        # Google Trends has no key; pytrends works unauthenticated. SERPAPI_KEY
        # enables a more robust provider. Either way, dry-run returns samples.
        if not settings.serpapi_key:
            return self._sample(brands)
        # TODO(live): pytrends/SerpApi rising queries for each seed topic.
        return self._sample(brands)

    def _sample(self, brands: dict) -> list[Signal]:
        return [
            Signal(self.NAME, "antarctica penguin chicks", "polar", 100, 0.72, _NOW(),
                   {"trend": "rising", "note": "sample"}),
            Signal(self.NAME, "best time to see penguins antarctica", "polar", 100, 0.58, _NOW(),
                   {"trend": "rising", "note": "sample"}),
        ]
