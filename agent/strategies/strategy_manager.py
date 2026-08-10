from __future__ import annotations

from typing import Any

from agent.strategies.baseline_strategy import BaselineStrategy
from agent.strategies.competitive_strategy import CompetitiveStrategy
from agent.strategies.economic_strategy import EconomicStrategy
from agent.strategies.market_strategy import MarketAwareStrategy
from agent.strategies.planning_strategy import PlanningStrategy
from agent.strategies.strategy import Strategy
from agent.strategies.strategy_registry import register

_STRATEGIES: dict[str, type[Strategy]] = {
    "baseline": BaselineStrategy,
    "economic": EconomicStrategy,
    "market_aware": MarketAwareStrategy,
    "planning": PlanningStrategy,
    "competitive": CompetitiveStrategy,
}

for name, cls in _STRATEGIES.items():
    register(name, cls)


class StrategyManager:
    """Manages strategy selection and lifecycle."""

    def __init__(self) -> None:
        self._active_strategies: dict[str, Strategy] = {}
        self._current_strategy: str = "baseline"

    def get_strategy(self, name: str) -> Strategy:
        if name not in self._active_strategies:
            cls = _STRATEGIES.get(name)
            if cls is None:
                cls = _STRATEGIES["baseline"]
            self._active_strategies[name] = cls()
        return self._active_strategies[name]

    def get_current_strategy(self) -> Strategy:
        return self.get_strategy(self._current_strategy)

    def set_current_strategy(self, name: str) -> None:
        self._current_strategy = name

    def list_strategies(self) -> list[str]:
        return list(_STRATEGIES.keys())

    def register_strategy(self, name: str, cls: type[Strategy]) -> None:
        _STRATEGIES[name] = cls
        register(name, cls)


_strategy_manager: StrategyManager | None = None


def get_default_strategy_manager() -> StrategyManager:
    global _strategy_manager
    if _strategy_manager is None:
        _strategy_manager = StrategyManager()
    return _strategy_manager


def get_strategy(name: str) -> Strategy:
    return _STRATEGIES.get(name, BaselineStrategy)()


def evaluate_all(
    context: Any,
    actions: list[Any],
) -> dict[str, list[Any]]:
    results: dict[str, list[Any]] = {}
    for name, cls in _STRATEGIES.items():
        strategy = cls()
        results[name] = strategy.evaluate(context, actions)
    return results


def list_strategies() -> list[str]:
    return list(_STRATEGIES.keys())


def register_strategy(name: str, cls: type[Strategy]) -> None:
    _STRATEGIES[name] = cls
    register(name, cls)
