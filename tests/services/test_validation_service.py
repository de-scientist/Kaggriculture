from agent.services import validation_service


def test_validate_valid_action():
    assert validation_service.validate(["PASS"], None) is True


def test_validate_empty_action():
    assert validation_service.validate([], None) is False


def test_validate_non_list():
    assert validation_service.validate("PASS", None) is False


def test_validate_action_valid():
    result = validation_service.validate_action(["PASS"], None)
    assert result.is_valid is True


def test_validate_action_invalid():
    result = validation_service.validate_action([], None)
    assert result.is_valid is False
    assert len(result.errors) > 0


def test_validate_state_valid():
    assert validation_service.validate_state(object()) is True


def test_validate_state_none():
    assert validation_service.validate_state(None) is False
