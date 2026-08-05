from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class Resource:
    def __init__(self, name: str, base_price: int):
        self.name = name
        self.base_price = base_price

    def __eq__(self, other):
        return isinstance(other, Resource) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


@dataclass
class PlantTile:
    kind: str = "PLANT"
    crop: str = ""
    planted_day: int = 0
    watered_today: bool = False
    consecutive_unwatered: int = 0
    yield_units: int = 0
    max_lifespan_step: int = -1
    fertilized_until_day: int = -1


@dataclass
class WeedTile:
    kind: str = "WEED"


@dataclass
class StructureTile:
    kind: str = ""
    animal: Optional[str] = None
    placed_day: int = 0
    yield_units: int = 0
    fed_today: bool = False
    consecutive_unfed: int = 0
    cared_today: bool = False
    fertilizer_available: bool = False
    pending_care_bonus: int = 0