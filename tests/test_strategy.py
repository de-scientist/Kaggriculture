from agent.strategies import baseline_strategy, strategy


def test_baseline_is_strategy():
    s = baseline_strategy.BaselineStrategy()
    assert isinstance(s, strategy.Strategy)
