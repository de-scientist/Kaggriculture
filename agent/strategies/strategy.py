from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class ScoredAction:
    __slots__ = ("action", "explanation", "score")

    def __init__(
        self,
        action: CandidateAction,
        score: float,
        explanation: str = "",
    ) -> None:
        self.action = action
        self.score = score
        self.explanation = explanation

    def __lt__(self, other: "ScoredAction") -> bool:
        return self.score < other.score

    def __le__(self, other: "ScoredAction") -> bool:
        return self.score <= other.score

    def __gt__(self, other: "ScoredAction") -> bool:
        return self.score > other.score

    def __ge__(self, other: "ScoredAction") -> bool:
        return self.score >= other.score


class Strategy(ABC):
    @abstractmethod
    def evaluate(
        self,
        context: DecisionContext,
        actions: list[CandidateAction],
    ) -> list[ScoredAction]:
        """Evaluate actions using the strategy's scoring logic."""
        ...


class BaselineStrategy(Strategy):
    def evaluate(
        self,
        context: DecisionContext,
        actions: list[CandidateAction],
    ) -> list[ScoredAction]:
        scored: list[ScoredAction] = []
        for action in actions:
            score, explanation = score_action(action)
            priority = get_priority(action.action_type)
            explanation = f"priority={priority}, {explanation}"
            scored.append(ScoredAction(action, score, explanation))
        scored.sort(key=lambda s: (-s.score, get_priority(s.action.action_type), s.action.id))
        return scored


def score_action(action: CandidateAction) -> tuple[float, str]:
    """Compute the base score for an action."""
    profit = max(0.0, action.estimated_reward)
    worker = 1.0 if action.worker else 0.5
    time_eff = 1.0 if action.action_type.lower() in ("harvest", "sell", "feed") else 0.7
    inventory = 0.5 if action.estimated_reward > 0 else 0.0
    market = 1.0 if action.action_type.lower() in ("sell", "buy_product") else 0.2
    sustainability = 0.5 if action.estimated_cost <= 0 else 0.5
    cost_penalty = -action.estimated_cost * 0.5
    opp_cost = -abs(action.estimated_reward - action.estimated_cost) * 0.2

    total = (
        profit * 1.0
        + worker * 0.3
        + time_eff * 0.2
        + inventory * 0.15
        + market * 0.25
        + sustainability * 0.1
        + cost_penalty
        + opp_cost
    )
    return total, f"profit={profit:.1f}, worker={worker:.1f}, time={time_eff:.1f}, inv={inventory:.1f}, market={market:.1f}, sustain={sustainability:.1f}, cost_penalty={cost_penalty:.1f}"


def get_priority(action_type: str) -> int:
    PRIORITY_MAP = {
        "harvest": 1,
        "collect": 2,
        "feed": 3,
        "water": 4,
        "fertilize": 5,
        "plant": 6,
        "sell": 7,
        "buy": 8,
        "hire": 9,
        "expand": 10,
        "pass": 11,
    }
    return PRIORITY_MAP.get(action_type.lower(), 11)