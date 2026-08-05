from agent.strategies import baseline_strategy
from agent.strategies import strategy


def test_baseline_is_strategy():
    s = baseline_strategy.BaselineStrategy()
    assert isinstance(s, strategy.Strategy)