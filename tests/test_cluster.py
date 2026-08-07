from trendengine.cluster import cluster
from trendengine.config_loader import load_brands
from trendengine.models import Signal


def _sig(source, entity, brand="galapagos"):
    return Signal(source, entity, brand, 1.0, 0.0, "t")


def test_destination_token_alone_does_not_merge_distinct_intents():
    """All four share 'galapagos' but are different intents — must NOT be one trend."""
    brands = load_brands()
    signals = [
        _sig("ahrefs_search", "galapagos cruise"),
        _sig("gsc", "galapagos wildlife march"),
        _sig("social", "galapagos family vlog"),
        _sig("news", "galapagos ship refurbishment"),
    ]
    trends = cluster(signals, brands)
    # No mega-cluster: nothing should claim 4-source corroboration.
    assert max(t.source_count for t in trends) < 4


def test_genuine_shared_intent_corroborates_across_sources():
    """Two sources both about the *cruise* intent should cluster -> 2 sources."""
    brands = load_brands()
    signals = [
        _sig("ahrefs_search", "galapagos cruise"),
        _sig("brandradar", "which galapagos cruise is best for families"),
        _sig("gsc", "galapagos wildlife march"),
    ]
    trends = cluster(signals, brands)
    cruise = [t for t in trends if "cruise" in t.title]
    assert cruise and cruise[0].source_count == 2
