import yaml
from pathlib import Path

from trendengine.config_loader import load_brands, load_weights
from trendengine.models import Signal, Trend
from trendengine.score import FACTORS, score_trend

WEIGHTS_PATH = Path("src/trendengine/config/weights.yaml")


def test_weights_keys_match_factors_and_sum_to_one():
    data = yaml.safe_load(WEIGHTS_PATH.read_text())
    assert set(data["weights"].keys()) == set(FACTORS)
    assert abs(sum(data["weights"].values()) - 1.0) < 1e-6


def test_score_is_bounded_and_uses_factors():
    weights, brands = load_weights(), load_brands()
    sigs = [
        Signal("ahrefs_search", "antarctica cruise", "polar", 4400, 0.61, "t"),
        Signal("google_trends", "antarctica cruise", "polar", 100, 0.58, "t"),
    ]
    t = score_trend(Trend("antarctica cruise", "polar", sigs), weights, brands)
    assert 0.0 <= t.score <= 100.0
    assert set(t.factors.keys()) == set(FACTORS)


def test_high_momentum_corroborated_trend_scores_well():
    weights, brands = load_weights(), load_brands()
    sigs = [
        Signal("google_trends", "antarctica cruise", "polar", 100, 0.72, "t"),
        Signal("social", "antarctica cruise", "polar", 250000, 0.90, "t"),
    ]
    t = score_trend(Trend("antarctica cruise", "polar", sigs), weights, brands)
    assert t.score >= weights["thresholds"]["min_score_to_brief"]
