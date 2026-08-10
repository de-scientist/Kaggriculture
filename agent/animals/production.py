from typing import Any


def compute_yield(animal: dict[str, Any], cared: bool) -> int:
    base = 1
    if cared:
        base += 1
    return base


def apply_care_bonus(animal: dict[str, Any]) -> dict[str, Any]:
    animal["pending_care_bonus"] = 1
    return animal
