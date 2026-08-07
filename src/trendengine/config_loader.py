"""Load YAML config (weights, brands) with light validation."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).parent / "config"


def _read_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config {name} must be a mapping, got {type(data)}")
    return data


def load_weights() -> dict[str, Any]:
    data = _read_yaml("weights.yaml")
    if "weights" not in data or "thresholds" not in data:
        raise ValueError("weights.yaml must define 'weights' and 'thresholds'")
    return data


def load_brands() -> dict[str, Any]:
    return _read_yaml("brands.yaml")
