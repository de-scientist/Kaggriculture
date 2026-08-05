from dataclasses import dataclass, field
from typing import Any


@dataclass
class Farm:
    money: float = 0.0
    tiles: list = field(default_factory=list)
    farmer: list = field(default_factory=list)
    hands: list = field(default_factory=list)
    unlocked_quadrants: list = field(default_factory=list)
    hires_today: int = 0