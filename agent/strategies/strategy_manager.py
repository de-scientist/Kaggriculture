from agent.strategies import baseline_strategy
from agent.strategies import strategy


_STRATEGIES = {
    "baseline": baseline_strategy.BaselineStrategy,
}


def get_strategy(config: dict) -> strategy.Strategy:
    name = config.get("strategy", {}).get("name", "baseline")
    cls = _STRATEGIES.get(name, baseline_strategy.BaselineStrategy)
    return cls()