from dataclasses import dataclass


@dataclass
class Animal:
    kind: str = ""
    animal: str = ""
    placed_day: int = -1
    yield_units: int = 0
    fed_today: bool = False
    consecutive_unfed: int = 0
    cared_today: bool = False
    fertilizer_available: bool = False
    pending_care_bonus: int = 0
