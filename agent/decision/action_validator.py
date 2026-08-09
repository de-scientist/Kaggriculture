from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    action: CandidateAction
    is_valid: bool
    failure_reasons: tuple[str, ...] = ()


def validate_action(
    action: CandidateAction,
    game_state: Any,
) -> ValidationResult:
    reasons: list[str] = []

    if action.action_type.lower() in ("plant", "water", "harvest", "fertilize"):
        if action.target_position is None:
            reasons.append("Target position required for tile action")

    if action.action_type.lower() in ("buy_seed", "buy_product", "buy_animal"):
        if action.estimated_cost > 0:
            if game_state is not None:
                money = getattr(game_state, "available_money", lambda: 0.0)()
                if action.estimated_cost > money:
                    reasons.append("Insufficient funds")

    if action.action_type.lower() == "hire":
        if game_state is not None:
            farm = getattr(game_state, "farm", None)
            if farm is not None:
                hires = getattr(farm, "hires_today", 0)
                if hires >= 10:
                    reasons.append("Maximum hires reached")

    is_valid = len(reasons) == 0
    return ValidationResult(
        action=action,
        is_valid=is_valid,
        failure_reasons=tuple(reasons),
    )


def validate_actions(
    actions: list[CandidateAction],
    game_state: Any,
) -> list[ValidationResult]:
    return [validate_action(a, game_state) for a in actions]