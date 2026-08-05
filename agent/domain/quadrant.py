from dataclasses import dataclass


@dataclass
class Quadrant:
    name: str = "NW"
    unlocked: bool = False
    cost: int = 0