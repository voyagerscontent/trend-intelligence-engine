"""Social & cultural listening (YouTube, Reddit, X/TikTok providers)."""
from __future__ import annotations

from datetime import datetime, timezone

from ..models import Signal
from ..settings import Settings

_NOW = lambda: datetime.now(timezone.utc).isoformat()


class SocialSource:
    NAME = "social"

    def fetch(self, settings: Settings, brands: dict) -> list[Signal]:
        if not (settings.youtube_api_key or settings.reddit_client_id):
            return self._sample(brands)
        # TODO(live): YouTube Data search+statistics, Reddit rising in relevant
        # subs; detect surging themes, creators and formats -> Signal.
        return self._sample(brands)

    def _sample(self, brands: dict) -> list[Signal]:
        return [
            Signal(self.NAME, "antarctica penguin chicks", "polar", 250000, 0.90, _NOW(),
                   {"format": "short-form video", "platform": "youtube", "note": "sample surge"}),
            Signal(self.NAME, "galapagos family trip vlog", "galapagos", 80000, 0.35, _NOW(),
                   {"format": "vlog", "platform": "youtube", "note": "sample"}),
        ]
