from agent.decision import decision_context


def rank(candidates: list, context: decision_context.DecisionContext) -> list:
    return sorted(candidates, key=lambda _a: 0)