"""Competitor & PR moves from Google News / RSS / a news API."""
from __future__ import annotations

from datetime import datetime, timezone

from ..models import Signal
from ..settings import Settings

_NOW = lambda: datetime.now(timezone.utc).isoformat()


class NewsSource:
    NAME = "news"

    def fetch(self, settings: Settings, brands: dict) -> list[Signal]:
        if not settings.news_api_key:
            return self._sample(brands)
        # TODO(live): query news API / RSS for brand + competitor names and
        # destination terms; new competitor coverage -> Signal.
        return self._sample(brands)

    def _sample(self, brands: dict) -> list[Signal]:
        return [
            Signal(self.NAME, "new antarctica expedition ship launch", "voyagers", 12, 0.45, _NOW(),
                   {"outlet": "trade press", "competitor": True, "note": "sample"}),
        ]
