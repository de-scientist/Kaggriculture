from __future__ import annotations

from typing import Any

from agent.strategies.strategy import Strategy
from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext


class PlanningStrategy(Strategy):
    """Planning-based strategy that generates multi-turn plans."""

    def __init__(self):
        self._planner = Planner(config=PlannerConfig(horizon_turns=5))

    def evaluate(
        self,
        context: DecisionContext,
        actions: list[CandidateAction],
    ) -> list[ScoredAction]:
        try:
            plan = self._planner.plan(context, actions, context.game_state)
            scored = [
                ScoredAction(
                    action=action,
                    score=self._evaluate_plan(plan, action),
                    explanation=f"plan_depth={plan.depth}",
                )
                for action in actions
            ]
            scored.sort(key=lambda s: (-s.score, get_priority(s.action.action_type), s.action.id))
            return scored
        except Exception:
            return BaselineStrategy().evaluate(context, actions)

    def _evaluate_plan(
        self,
        plan: Plan,
        action: CandidateAction,
    ) -> float:
        return 0.0