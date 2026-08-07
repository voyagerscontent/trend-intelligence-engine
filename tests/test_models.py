from trendengine.models import Signal, Trend


def test_signal_key_is_stable_and_case_insensitive():
    a = Signal("ahrefs_search", "Antarctica Trips", "voyagers", 1, 0.0, "t")
    b = Signal("ahrefs_search", "antarctica trips ", "voyagers", 1, 0.0, "t")
    assert a.key() == b.key()


def test_trend_source_count_counts_distinct_sources():
    sigs = [
        Signal("a", "x", "polar", 1, 0.0, "t"),
        Signal("b", "x", "polar", 1, 0.0, "t"),
        Signal("a", "x", "polar", 1, 0.0, "t"),
    ]
    assert Trend("x", "polar", sigs).source_count == 2
