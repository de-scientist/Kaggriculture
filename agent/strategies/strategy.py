from abc import ABC, abstractmethod
from agent.decision import decision_context


class Strategy(ABC):
    @abstractmethod
    def rank(self, candidates: list, context: decision_context.DecisionContext) -> list:
        ...