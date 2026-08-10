from __future__ import annotations

from typing import Any

from agent.decision.baseline_strategy import BaselineStrategy
from agent.decision.strategy import Strategy

_STRATEGIES = {
    "baseline": BaselineStrategy,
}


def get_strategy(config: dict[str, Any]) -> Strategy:
    name = config.get("strategy", {}).get("name", "baseline")
    cls = _STRATEGIES.get(name, BaselineStrategy)
    return cls()
