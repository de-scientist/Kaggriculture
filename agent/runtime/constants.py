"""Static game data mirroring the kaggriculture engine.

The planner reasons over crop/animal/market economics without importing
``kaggle_environments``, so this module reproduces the engine's default
constants (they are only overridden through competition configuration).
"""

from __future__ import annotations

from typing import TypedDict


class CropSpec(TypedDict):
    seed: int
    first_yield_day: int
    max_yield_day: int
    interval: int
    max_yield: int
    ongoing: bool


CROPS: dict[str, CropSpec] = {
    "WHEAT": {
        "seed": 10,
        "first_yield_day": 2,
        "max_yield_day": 4,
        "interval": 0,
        "max_yield": 6,
        "ongoing": False,
    },
    "CARROT": {
        "seed": 20,
        "first_yield_day": 2,
        "max_yield_day": 3,
        "interval": 0,
        "max_yield": 4,
        "ongoing": False,
    },
    "TOMATO": {
        "seed": 50,
        "first_yield_day": 8,
        "max_yield_day": 8,
        "interval": 1,
        "max_yield": 4,
        "ongoing": True,
    },
    "STRAWBERRY": {
        "seed": 100,
        "first_yield_day": 10,
        "max_yield_day": 10,
        "interval": 2,
        "max_yield": 4,
        "ongoing": True,
    },
    "MELON": {
        "seed": 80,
        "first_yield_day": 10,
        "max_yield_day": 12,
        "interval": 0,
        "max_yield": 6,
        "ongoing": False,
    },
}


class AnimalSpec(TypedDict):
    cost: int
    structure: str
    first_yield_day: int
    interval: int
    max_held: int
    product: str


ANIMALS: dict[str, AnimalSpec] = {
    "GOOSE": {
        "cost": 300,
        "structure": "COOP",
        "first_yield_day": 4,
        "interval": 1,
        "max_held": 4,
        "product": "EGG",
    },
    "COW": {
        "cost": 400,
        "structure": "PASTURE",
        "first_yield_day": 8,
        "interval": 2,
        "max_held": 6,
        "product": "MILK",
    },
    "SHEEP": {
        "cost": 500,
        "structure": "PASTURE",
        "first_yield_day": 6,
        "interval": 3,
        "max_held": 6,
        "product": "WOOL",
    },
}

PRODUCTS: list[str] = [
    "WHEAT",
    "CARROT",
    "TOMATO",
    "STRAWBERRY",
    "MELON",
    "EGG",
    "MILK",
    "WOOL",
    "FERTILIZER",
]

ANIMAL_PRODUCTS: list[str] = ["EGG", "MILK", "WOOL"]


class MarketSpec(TypedDict):
    base: int
    I0: int
    T: int
    below_func: str
    below_target: float
    above_func: str
    above_target: float


MARKET: dict[str, MarketSpec] = {
    "WHEAT": {
        "base": 25,
        "I0": 10000,
        "T": 400,
        "below_func": "sqrt",
        "below_target": 0.80,
        "above_func": "log",
        "above_target": 0.20,
    },
    "CARROT": {
        "base": 35,
        "I0": 10000,
        "T": 450,
        "below_func": "log",
        "below_target": 0.20,
        "above_func": "sqrt",
        "above_target": 0.70,
    },
    "TOMATO": {
        "base": 60,
        "I0": 10000,
        "T": 200,
        "below_func": "linear",
        "below_target": 0.40,
        "above_func": "sqrt",
        "above_target": 0.60,
    },
    "STRAWBERRY": {
        "base": 120,
        "I0": 10000,
        "T": 100,
        "below_func": "sqrt",
        "below_target": 0.70,
        "above_func": "linear",
        "above_target": 1.60,
    },
    "MELON": {
        "base": 250,
        "I0": 10000,
        "T": 300,
        "below_func": "log",
        "below_target": 0.20,
        "above_func": "sq",
        "above_target": 3.60,
    },
    "EGG": {
        "base": 50,
        "I0": 10000,
        "T": 332,
        "below_func": "linear",
        "below_target": 0.40,
        "above_func": "log",
        "above_target": 0.20,
    },
    "MILK": {
        "base": 160,
        "I0": 10000,
        "T": 122,
        "below_func": "sqrt",
        "below_target": 0.60,
        "above_func": "linear",
        "above_target": 1.60,
    },
    "WOOL": {
        "base": 200,
        "I0": 10000,
        "T": 105,
        "below_func": "log",
        "below_target": 0.20,
        "above_func": "sq",
        "above_target": 3.20,
    },
    "FERTILIZER": {
        "base": 100,
        "I0": 10000,
        "T": 200,
        "below_func": "linear",
        "below_target": 0.40,
        "above_func": "linear",
        "above_target": 0.40,
    },
}

SHOP_DEMAND: dict[str, list[str]] = {
    "BAKERY": ["EGG", "WHEAT"],
    "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE": ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
    "PET_CAFE": ["CARROT"],
    "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}

FARMER_MOVES: dict[str, tuple[int, int]] = {
    "NORTH": (0, -1),
    "SOUTH": (0, 1),
    "EAST": (1, 0),
    "WEST": (-1, 0),
}

LAND_ORDER: list[str] = ["NE", "SW", "SE"]
LAND_PRICES: list[int] = [1000, 2000, 4000]

FARM_HAND_FIB: list[int] = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

SHED_CAPACITY: int = 100
BOARD_SIZE_DEFAULT: int = 10
TURNS_PER_DAY_DEFAULT: int = 24
EPISODE_STEPS_DEFAULT: int = 720

FARM_HAND_COST_MULT: int = 1


def hire_cost(n_already_hired: int, mult: float = FARM_HAND_COST_MULT) -> int:
    """Cost of the next hire given how many hands were hired today."""
    if n_already_hired < 0:
        n_already_hired = 0
    if n_already_hired < len(FARM_HAND_FIB):
        return round(mult * FARM_HAND_FIB[n_already_hired])
    a, b = 1, 1
    for _ in range(n_already_hired):
        a, b = b, a + b
    return round(mult * a)


def window_start_day(crop: str) -> int:
    """First day (inclusive) of the watering bonus window for one-time crops."""
    return (int(CROPS[crop]["max_yield_day"]) + 1) // 2


def window_end_day(crop: str) -> int:
    return int(CROPS[crop]["max_yield_day"])


def is_ongoing(crop: str) -> bool:
    return bool(CROPS[crop]["ongoing"])


def product_of(animal: str) -> str:
    return str(ANIMALS[animal]["product"])


def structure_of(animal: str) -> str:
    return str(ANIMALS[animal]["structure"])


def crop_base_price(crop: str) -> int:
    return int(MARKET[crop]["base"])
