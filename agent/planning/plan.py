"""Stage 2 — Plan representation.

A plan is a sequence of actions with an expected value estimate.
Plans are constructed by the planner and consumed by the decision engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PlanStep:
    """A single step within a plan."""

    turn: int
    action_type: str
    target_position: tuple[int, int] | None = None
    target_entity: str = ""
    params: dict[str, Any] = field(default_factory=dict)

    @property
    def worker_op(self) -> tuple[str, ...]:
        if self.action_type in ("plant", "water", "harvest", "fertilize", "dig", "feed", "care"):
            return (self.action_type.upper(),)
        elif self.action_type in ("build_coop", "build_pasture"):
            return (self.action_type.upper(),)
        elif self.action_type == "pass":
            return ("PASS",)
        elif self.action_type.startswith("move_"):
            return (self.action_type.replace("move_", "").upper(),)
        elif self.action_type == "pickup":
            return ("PICKUP", self.target_entity)
        elif self.action_type == "place":
            return ("PLACE", self.target_entity)
        elif self.action_type == "drop":
            return ("DROP",)
        return ("PASS",)


@dataclass
class Plan:
    """A multi-turn action plan with expected value."""

    steps: list[PlanStep] = field(default_factory=list)
    expected_value: float = 0.0
    expected_profit: float = 0.0
    required_capital: float = 0.0
    required_workers: int = 1
    completion_turns: int = 0
    confidence: float = 0.5
    risk: float = 0.0
    description: str = ""

    def add_step(self, step: PlanStep) -> None:
        self.steps.append(step)
        self.completion_turns = max(self.completion_turns, step.turn)

    @property
    def first_action(self) -> tuple[str, ...] | None:
        if not self.steps:
            return None
        return self.steps[0].worker_op

    @property
    def value_per_turn(self) -> float:
        if self.completion_turns <= 0:
            return 0.0
        return self.expected_value / self.completion_turns

    def to_action_dict(self, remaining_steps: list[PlanStep] | None = None) -> dict[str, Any]:
        """Convert the first step to a Kaggle action dict."""
        steps = remaining_steps if remaining_steps is not None else self.steps
        if not steps:
            return {"farmer": ["PASS"], "hands": [], "market": []}

        first = steps[0]
        farmer_op = list(first.worker_op)
        return {
            "farmer": farmer_op,
            "hands": [],
            "market": [],
        }

    def is_feasible(
        self,
        available_cash: float,
        available_workers: int,
        remaining_turns: int,
    ) -> bool:
        return (
            self.required_capital <= available_cash
            and self.required_workers <= available_workers
            and self.completion_turns <= remaining_turns
        )


@dataclass
class PlanEvaluation:
    """Result of evaluating a plan against the current state."""

    plan: Plan
    is_feasible: bool
    is_legal: bool
    total_score: float
    immediate_score: float
    future_value: float
    explanation: str = ""
