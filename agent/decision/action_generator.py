from agent.decision import decision_context


def generate_candidates(context: decision_context.DecisionContext) -> list:
    candidates = []
    candidates.append({"farmer": ["PASS"], "hands": [], "market": []})
    return candidates