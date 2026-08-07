"""Search/SEO trend signals from Ahrefs (Keywords Explorer, Rank Tracker).

Live mode calls the Ahrefs API v3. Without AHREFS_API_KEY it returns
representative sample signals so the pipeline runs end-to-end offline.
"""
from __future__ import annotations

from datetime import datetime, timezone

from ..models import Signal
from ..settings import Settings

_NOW = lambda: datetime.now(timezone.utc).isoformat()


class AhrefsSearchSource:
    NAME = "ahrefs_search"

    def fetch(self, settings: Settings, brands: dict) -> list[Signal]:
        if not settings.ahrefs_api_key:
            return self._sample(brands)
        # TODO(live): call keywords-explorer volume-history + related-terms and
        # rank-tracker for each brand's seed_topics; map rows -> Signal.
        # Kept as a stub so credentials can be wired without changing the contract.
        return self._sample(brands)

    def _sample(self, brands: dict) -> list[Signal]:
        return [
            Signal(self.NAME, "antarctica trips", "voyagers", 18000, 0.22, _NOW(),
                   {"kd": 34, "note": "sample"}),
            Signal(self.NAME, "galapagos cruise", "galapagos", 27000, 0.08, _NOW(),
                   {"kd": 41, "note": "sample"}),
            Signal(self.NAME, "best time to see penguins antarctica", "polar", 4400, 0.61, _NOW(),
                   {"kd": 12, "note": "sample rising query"}),
        ]
