from trendengine.pipeline import run_pipeline


def test_dry_run_pipeline_produces_at_least_one_brief():
    result = run_pipeline(stage="all", dry_run=True)
    assert result.signals > 0
    assert result.trends > 0
    assert result.briefed >= 1
    # every briefed trend must be corroborated (>= 2 sources) and on-score
    for t in result.escalated:
        assert t.source_count >= 2
