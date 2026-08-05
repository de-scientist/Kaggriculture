def compute_age(planted_day: int, current_day: int) -> int:
    return current_day - planted_day


def is_mature(crop: str, age: int) -> bool:
    return age >= 2


def compute_yield(crop: str, age: int, watered: bool, fertilized: bool) -> int:
    base = 1
    if watered:
        base += 1
    if fertilized:
        base += 1
    return base
