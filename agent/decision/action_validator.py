from agent.decision import decision_context


def validate(action: dict, context: decision_context.DecisionContext) -> bool:
    if not isinstance(action, dict):
        return False
    if "farmer" not in action:
        return False
    if "hands" not in action:
        return False
    if "market" not in action:
        return False
    return True