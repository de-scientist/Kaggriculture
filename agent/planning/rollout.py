from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RolloutResult:
    plan: Plan
    expected_value: float
    risk: float
    confidence: float
    simulated_state: Any
    rollout_iterations: int


class RolloutEngine:
    """Rollout engine for estimating future outcomes of candidate plans."""

    def __init__(self, config: dict | None = None):
        self.max_rollouts = config.get("max_rollouts", 10) if config else 10
        self.max_branching = config.get("max_branching", 8) if config else 8

    def rollouts(
        self,
        current_state: Any,
        candidate_actions: list[dict],
        horizon: int,
    ) -> list[RolloutResult]:
        results = []
        for _ in range(self.max_rollouts):
            result = self._simulate_rollout(
                current_state=current_state,
                candidate_actions=candidate_actions,
                horizon=horizon,
            )
            results.append(result)
        return results

    def _simulate_rollout(
        self,
        current_state: Any,
        candidate_actions: list[dict],
        horizon: int,
    ) -> RolloutResult:
        return RolloutResult(
            plan=Plan(),
            expected_value=0.0,
            risk=0.0,
            confidence=0.5,
            simulated_state=current_state,
            rollout_iterations=0,
        )
