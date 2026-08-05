from dataclasses import dataclass


@dataclass
class Tile:
    kind: str = "EMPTY"
    crop: str | None = None
    planted_day: int = -1
    watered_today: bool = False
    consecutive_unwatered: int = 0
    yield_units: int = 0
    max_lifespan_step: int = 0
    fertilized_until_day: int = -1
