"""Your own rising queries and impressions from Google Search Console."""
from __future__ import annotations

from datetime import datetime, timezone

from ..models import Signal
from ..settings import Settings

_NOW = lambda: datetime.now(timezone.utc).isoformat()


class GscSource:
    NAME = "gsc"

    def fetch(self, settings: Settings, brands: dict) -> list[Signal]:
        if not settings.gsc_credentials:
            return self._sample(brands)
        # TODO(live): Search Console API searchanalytics.query, dimension=query,
        # compare trailing 28d vs prior 28d -> change_pct.
        return self._sample(brands)

    def _sample(self, brands: dict) -> list[Signal]:
        return [
            Signal(self.NAME, "galapagos wildlife march", "galapagos", 900, 0.55, _NOW(),
                   {"impressions": 12000, "note": "sample"}),
        ]
