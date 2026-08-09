from __future__ import annotations

from agent.strategies.strategy import Strategy, ScoredAction
from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.strategies.priorities import get_priority
from agent.strategies.scoring import score_action


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