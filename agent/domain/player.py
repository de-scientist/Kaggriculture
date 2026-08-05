from dataclasses import dataclass, field
from typing import Any


@dataclass
class Player:
    index: int
    money: float = 0.0
    farm: Any = None
    shed: dict = field(default_factory=dict)
    seeds: dict = field(default_factory=dict)
    inventories: list = field(default_factory=list)
