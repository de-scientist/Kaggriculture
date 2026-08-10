from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SimulationState:
    state: Any
    action: dict[str, Any]
    next_state: Any
    trajectory: list[Any]
    expected_profit: float
    risk: float
    confidence: float
    cost: float
    reward: float


class SimulationEngine:
    """Lightweight simulation engine for planning."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.budget = config.get("budget", 10000) if config else 10000
        self.max_steps = config.get("max_steps", 100) if config else 100

    def simulate(
        self,
        initial_state: Any,
        actions: list[dict[str, Any]],
        horizon: int,
    ) -> list[SimulationState]:
        states: list[SimulationState] = []
        for i in range(horizon):
            if i >= self.max_steps:
                break
            sim = self._step(
                initial_state=initial_state,
                action=actions[i] if i < len(actions) else None,
                horizon=horizon,
            )
            states.append(sim)
        return states

    def _step(
        self,
        initial_state: Any,
        action: dict[str, Any] | None,
        horizon: int,
    ) -> SimulationState:
        return SimulationState(
            state=initial_state,
            action=action,
            next_state=initial_state,
            trajectory=[],
            expected_profit=0.0,
            risk=0.0,
            confidence=0.5,
            cost=0.0,
            reward=0.0,
        )
