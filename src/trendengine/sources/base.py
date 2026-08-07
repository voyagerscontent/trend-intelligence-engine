"""The source contract every signal source must satisfy."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import Signal
from ..settings import Settings


@runtime_checkable
class SignalSource(Protocol):
    #: Unique, snake_case identifier. Must be unique across the REGISTRY.
    NAME: str

    def fetch(self, settings: Settings, brands: dict) -> list[Signal]:
        """Return a list of Signal objects.

        Implementations MUST:
          * return [] rather than raise on a recoverable API error, and
          * fall back to representative sample signals when their credential
            is absent (dry-run), so the full pipeline is testable offline.
        """
        ...
