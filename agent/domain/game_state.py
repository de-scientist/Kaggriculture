from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameState:
    player: int
    day: int = 0
    hour: int = 0
    step: int = 0
    farms: list = field(default_factory=list)
    private: dict = field(default_factory=dict)
    market: dict = field(default_factory=dict)
    town: dict = field(default_factory=dict)