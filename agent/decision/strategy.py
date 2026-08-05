from __future__ import annotations

from abc import ABC, abstractmethod
from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext


class Strategy(ABC):
    @abstractmethod
    def rank(
        self,
        candidates: list[CandidateAction],
        context: DecisionContext,
    ) -> list[CandidateAction]:
        ...