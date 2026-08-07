from trendengine.models import Signal
from trendengine.config_loader import load_brands
from trendengine.settings import Settings
from trendengine.sources import REGISTRY


def test_every_source_returns_signals_in_dry_run():
    brands = load_brands()
    settings = Settings()  # no credentials -> dry-run
    for src in REGISTRY:
        out = src.fetch(settings, brands)
        assert isinstance(out, list)
        assert all(isinstance(s, Signal) for s in out)


def test_source_names_are_unique():
    names = [s.NAME for s in REGISTRY]
    assert len(names) == len(set(names))
