from __future__ import annotations

from abc import ABC, abstractmethod

from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext


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

    def __lt__(self, other: ScoredAction) -> bool:
        return self.score < other.score

    def __le__(self, other: ScoredAction) -> bool:
        return self.score <= other.score

    def __gt__(self, other: ScoredAction) -> bool:
        return self.score > other.score

    def __ge__(self, other: ScoredAction) -> bool:
        return self.score >= other.score


class Strategy(ABC):
    @abstractmethod
    def evaluate(
        self,
        context: DecisionContext,
        actions: list[CandidateAction],
    ) -> list[ScoredAction]:
        ...
