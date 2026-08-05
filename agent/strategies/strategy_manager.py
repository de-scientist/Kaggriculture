from agent.strategies import baseline_strategy, strategy

_STRATEGIES = {
    "baseline": baseline_strategy.BaselineStrategy,
}


def get_strategy(config: dict) -> strategy.Strategy:
    name = config.get("strategy", {}).get("name", "baseline")
    cls = _STRATEGIES.get(name, baseline_strategy.BaselineStrategy)
    return cls()
