from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


def validate(action: list, game_state: object | None) -> bool:
    if not isinstance(action, list) or len(action) == 0:
        return False
    return True


def validate_action(action: list, game_state: object | None) -> ValidationResult:
    errors: list[str] = []
    if not isinstance(action, list) or len(action) == 0:
        errors.append("Action must be a non-empty list")
        return ValidationResult(is_valid=False, errors=errors)
    return ValidationResult(is_valid=True, errors=errors)


def validate_state(game_state: object | None) -> bool:
    if game_state is None:
        return False
    return True
