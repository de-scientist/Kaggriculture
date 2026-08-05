from __future__ import annotations

from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.strategies.baseline_strategy import BaselineStrategy
from agent.strategies.strategy import ScoredAction, Strategy

_STRATEGIES: dict[str, type[Strategy]] = {
    "baseline": BaselineStrategy,
}


def register_strategy(name: str, cls: type[Strategy]) -> None:
    _STRATEGIES[name] = cls


def get_strategy(name: str) -> Strategy:
    cls = _STRATEGIES.get(name, BaselineStrategy)
    return cls()


def list_strategies() -> list[str]:
    return list(_STRATEGIES.keys())


def evaluate_all(
    context: DecisionContext,
    actions: list[CandidateAction],
) -> dict[str, list[ScoredAction]]:
    results: dict[str, list[ScoredAction]] = {}
    for name, cls in _STRATEGIES.items():
        strategy = cls()
        results[name] = strategy.evaluate(context, actions)
    return results
