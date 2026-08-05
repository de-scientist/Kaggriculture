from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class TileType(Enum):
    EMPTY = None
    LOCKED = "LOCKED"
    PLANT = "PLANT"
    WEED = "WEED"
    COOP = "COOP"
    PASTURE = "PASTURE"


@dataclass(frozen=True)
class Crop:
    crop_type: str
    seed_cost: int
    base_price: int
    first_yield_day: int
    max_yield_day: int
    max_yield: int
    base_daily_yield: int
    is_fertilizable: bool = True
    is_ongoing: bool = False
    interval_days: Optional[int] = None


@dataclass(frozen=True)
class Animal:
    animal_type: str
    cost: int
    base_price: int
    first_yield_day: int
    interval_days: int
    max_held: int
    structure_type: str
    product_type: str


@dataclass(frozen=True)
class Turn:
    day: int
    hour: int
    step: int = 0

    @property
    def is_last_hour(self) -> bool:
        return self.hour == 23


@dataclass(frozen=True)
class Season:
    turn_count: int
    turns_per_day: int = 24
    days: int = 30

    @property
    def current_day(self) -> int:
        return min(self.turn_count // self.turns_per_day, self.days - 1)

    @property
    def current_hour(self) -> int:
        return self.turn_count % self.turns_per_day


@dataclass
class Farm:
    owner: int
    board_size: int = 10
    money: float = 3000.0
    farmer_pos: List[int] = field(default_factory=lambda: [0, 0])
    hands: List[List[int]] = field(default_factory=list)
    unlocked_quadrants: List[str] = field(default_factory=lambda: ["NW"])
    hires_today: int = 0
    tiles: List[List[Any]] = field(default_factory=list)


@dataclass
class PlayerState:
    farm: Farm
    shed: Dict[str, int] = field(default_factory=dict)
    seeds: Dict[str, int] = field(default_factory=dict)
    field_inventory: Dict[str, int] = field(default_factory=dict)


@dataclass
class GameState:
    turn: Turn
    season: Season
    raw: Dict[str, Any] = field(default_factory=dict)
    self_player: int = 0
    opponent: int = 1
    public_farms: List[PlayerState] = field(default_factory=list)
    market: Dict[str, Any] = field(default_factory=dict)
    town: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)