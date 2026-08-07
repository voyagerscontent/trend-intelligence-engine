"""Signal sources.

Every module here exposes a class implementing the SignalSource protocol
(see base.py): a unique NAME and a fetch() returning list[Signal].
REGISTRY is the single place the pipeline discovers sources, so adding a
source is: create the module, then register it below.
"""
from __future__ import annotations

from .base import SignalSource
from .ahrefs_search import AhrefsSearchSource
from .ahrefs_brandradar import AhrefsBrandRadarSource
from .gsc import GscSource
from .google_trends import GoogleTrendsSource
from .social import SocialSource
from .news import NewsSource

REGISTRY: list[SignalSource] = [
    AhrefsSearchSource(),
    AhrefsBrandRadarSource(),
    GscSource(),
    GoogleTrendsSource(),
    SocialSource(),
    NewsSource(),
]

__all__ = ["SignalSource", "REGISTRY"]
