from __future__ import annotations

from agent.strategies.strategy import Strategy
from agent.strategies.baseline_strategy import BaselineStrategy
from agent.strategies.economic_strategy import EconomicStrategy
from agent.strategies.market_strategy import MarketAwareStrategy
from agent.strategies.planning_strategy import PlanningStrategy
from agent.strategies.competitive_strategy import CompetitiveStrategy
from agent.strategies.strategy_manager import StrategyManager


_STRATEGIES = {
    "baseline": BaselineStrategy,
    "economic": EconomicStrategy,
    "market_aware": MarketAwareStrategy,
    "planning": PlanningStrategy,
    "competitive": CompetitiveStrategy,
}


def get_strategy(name: str) -> Strategy:
    cls = _STRATEGIES.get(name, BaselineStrategy)
    return cls()


def is_registered(name: str) -> bool:
    return name in _STRATEGIES


def names() -> list[str]:
    return list(_STRATEGIES.keys())


def validate(name: str) -> bool:
    cls = _STRATEGIES.get(name)
    if cls is None:
        return False
    return issubclass(cls, Strategy)