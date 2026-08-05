from agent.decision import action_validator
from agent.decision.candidate_actions import CandidateAction


def test_validate_returns_valid_for_valid_action():
    action = CandidateAction(
        id="test_0",
        action_type="pass",
        estimated_cost=0.0,
        estimated_reward=0.0,
    )
    result = action_validator.validate_action(action, None)
    assert result.is_valid is True


def test_validate_returns_invalid_for_action_with_no_target():
    action = CandidateAction(
        id="test_1",
        action_type="plant",
        estimated_cost=10.0,
        estimated_reward=15.0,
    )
    result = action_validator.validate_action(action, None)
    assert result.is_valid is False
