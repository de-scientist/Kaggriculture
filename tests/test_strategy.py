from agent.strategies import baseline_strategy, strategy


def test_baseline_is_strategy() -> None:
    s = baseline_strategy.BaselineStrategy()
    assert isinstance(s, strategy.Strategy)
