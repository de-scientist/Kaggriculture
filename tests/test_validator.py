from agent.decision import action_validator
from agent.decision import decision_context


def test_validate_returns_true_for_valid_action():
    context = decision_context.DecisionContext(obs={}, player=0)
    action = {"farmer": ["PASS"], "hands": [], "market": []}
    assert action_validator.validate(action, context) is True