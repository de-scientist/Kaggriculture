def to_kaggle_format(action: dict) -> dict:
    result: dict = {
        "farmer": action.get("farmer", ["PASS"]),
        "hands": action.get("hands", []),
        "market": action.get("market", []),
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
