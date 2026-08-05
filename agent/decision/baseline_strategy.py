from __future__ import annotations

from agent.decision import utility_score
from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.decision.strategy import Strategy


class BaselineStrategy(Strategy):
    def rank(
        self,
        candidates: list[CandidateAction],
        context: DecisionContext,
    ) -> list[CandidateAction]:
        scored = [(utility_score.compute_utility(a), a) for a in candidates]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [a for _, a in scored]