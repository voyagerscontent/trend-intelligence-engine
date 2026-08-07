"""Normalise raw signals: dedupe identical observations, keep the strongest."""
from __future__ import annotations

from .models import Signal


def normalize(signals: list[Signal]) -> list[Signal]:
    best: dict[str, Signal] = {}
    for s in signals:
        k = s.key()
        cur = best.get(k)
        if cur is None or s.value > cur.value:
            best[k] = s
    return list(best.values())
