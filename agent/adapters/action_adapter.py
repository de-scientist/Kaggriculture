from agent.domain import action as action_domain


def to_kaggle_format(action: action_domain.Action) -> dict:
    result: dict = {
        "farmer": action.farmer_op,
        "hands": action.hand_ops,
        "market": action.market_ops,
    }
    return result


def validate(action_dict: dict) -> bool:
    if not isinstance(action_dict, dict):
        return False
    if "farmer" not in action_dict:
        return False
    if "hands" not in action_dict:
        return False
    if "market" not in action_dict:
        return False
    return True