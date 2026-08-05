def compute_yield(animal: dict, cared: bool) -> int:
    base = 1
    if cared:
        base += 1
    return base


def apply_care_bonus(animal: dict) -> dict:
    animal["pending_care_bonus"] = 1
    return animal
