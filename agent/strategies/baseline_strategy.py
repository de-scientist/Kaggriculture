from agent.decision import decision_context
from agent.strategies import strategy


class BaselineStrategy(strategy.Strategy):
    def rank(self, candidates: list, context: decision_context.DecisionContext) -> list:
        return candidates
