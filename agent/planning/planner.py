from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Plan:
    actions: list[dict] = field(default_factory=list)
    expected_profit: float = 0.0
    required_capital: float = 0.0
    required_workers: int = 0
    required_land: int = 0
    completion_time: int = 0
    risk: float = 0.0
    confidence: float = 0.0
    depth: int = 0


class Planner:
    """Multi-turn planner with configurable horizon."""

    def __init__(self, config: dict | None = None):
        self.horizon_turns = config.get("horizon_turns", 5) if config else 5
        self.max_rollouts = config.get("max_rollouts", 10) if config else 10
        self.max_branching = config.get("max_branching", 8) if config else 8
        self.enable_planning = config.get("enable_planning", True) if config else True

    def plan(
        self,
        context: Any,
        actions: list[dict],
        game_state: Any,
    ) -> Plan:
        """Generate a multi-turn plan."""
        if not self.enable_planning:
            return Plan()

        return self._greedy_plan(context, actions, game_state)

    def _greedy_plan(
        self,
        context: Any,
        actions: list[dict],
        game_state: Any,
    ) -> Plan:
        plan_actions: list[dict] = []
        expected_profit = 0.0
        required_capital = 0.0
        required_workers = 0
        required_land = 0
        completion_time = 0
        risk = 0.0
        confidence = 1.0
        depth = 0

        remaining_turns = context.remaining_turns if hasattr(context, "remaining_turns") else 720

        for i in range(self.horizon_turns):
            if i >= remaining_turns:
                break
            action = self._select_action(context, i, remaining_turns)
            if action:
                plan_actions.append(action)
                depth += 1

        return Plan(
            actions=plan_actions,
            expected_profit=expected_profit,
            required_capital=required_capital,
            required_workers=required_workers,
            required_land=required_land,
            completion_time=depth,
            risk=risk,
            confidence=confidence,
            depth=depth,
        )

    def _select_action(
        self,
        context: Any,
        turn: int,
        remaining_turns: int,
    ) -> dict | None:
        return None