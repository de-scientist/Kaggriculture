from agent.adapters.action_adapter import ActionAdapter


def test_convert_valid_action():
    adapter = ActionAdapter()
    action = {"farmer": ["PASS"], "hands": [], "market": []}
    result = adapter.convert(action)
    assert result["farmer"] == ["PASS"]


def test_convert_invalid_action():
    adapter = ActionAdapter()
    action = {"farmer": ["PASS"]}
    try:
        adapter.convert(action)
    except KeyError:
        pass
