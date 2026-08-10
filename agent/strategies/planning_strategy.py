from __future__ import annotations

from typing import Any

from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.planning.plan import Plan
from agent.planning.planner import Planner, PlannerConfig
from agent.strategies.baseline_strategy import BaselineStrategy
from agent.strategies.priorities import get_priority
from agent.strategies.strategy import ScoredAction, Strategy


class PlanningStrategy(Strategy):
    """Planning-based strategy that generates multi-turn plans."""

    def __init__(self) -> None:
        self._planner = Planner(config=PlannerConfig(horizon_turns=5))

    def evaluate(
        self,
        context: DecisionContext,
        actions: list[CandidateAction],
    ) -> list[ScoredAction]:
        try:
            plan = self._planner.plan(
                context.game_state,
                current_turn=context.step,
                total_turns=context.step + context.remaining_turns,
                available_cash=self._available_cash(context),
                context=context,
                actions=actions,
            )
            scored = [
                ScoredAction(
                    action=action,
                    score=self._evaluate_plan(plan, action),
                    explanation=f"plan_depth={len(plan.steps)}",
                )
                for action in actions
            ]
            scored.sort(key=lambda s: (-s.score, get_priority(s.action.action_type), s.action.id))
            return scored
        except Exception:
            return BaselineStrategy().evaluate(context, actions)

    def _evaluate_plan(self, plan: Plan, action: CandidateAction) -> float:
        plan_value = plan.expected_value if plan is not None else 0.0
        return plan_value * 0.5 + action.net_value * 0.5

    @staticmethod
    def _available_cash(context: DecisionContext) -> float:
        game_state = context.game_state
        if game_state is None:
            return 0.0
        money = getattr(game_state, "available_money", None)
        if callable(money):
            return float(money())
        return 0.0
