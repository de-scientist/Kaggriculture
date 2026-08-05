from agent.adapters import action_adapter


def test_validate_valid_action():
    action = {"farmer": ["PASS"], "hands": [], "market": []}
    assert action_adapter.validate(action) is True


def test_validate_invalid_action():
    action = {"farmer": ["PASS"]}
    assert action_adapter.validate(action) is False