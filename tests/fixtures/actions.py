"""Shared action fixtures for Kaggriculture tests."""
from __future__ import annotations


def pass_action() -> dict:
    return {"farmer": ["PASS"], "hands": [], "market": []}


def plant_action(crop: str = "WHEAT") -> dict:
    return {"farmer": ["PLANT", crop], "hands": [], "market": []}


def water_action() -> dict:
    return {"farmer": ["WATER"], "hands": [], "market": []}


def harvest_action() -> dict:
    return {"farmer": ["HARVEST"], "hands": [], "market": []}


def fertilize_action() -> dict:
    return {"farmer": ["FERTILIZE"], "hands": [], "market": []}


def dig_action() -> dict:
    return {"farmer": ["DIG"], "hands": [], "market": []}


def sell_action(item: str = "WHEAT", quantity: int = 1) -> dict:
    return {"farmer": ["PASS"], "hands": [], "market": [["SELL", item, quantity]]}


def buy_seed_action(crop: str = "WHEAT", quantity: int = 1) -> dict:
    return {"farmer": ["PASS"], "hands": [], "market": [["BUY_SEED", crop, quantity]]}


def buy_animal_action(animal: str = "GOOSE", quantity: int = 1) -> dict:
    return {"farmer": ["PASS"], "hands": [], "market": [["BUY_ANIMAL", animal, quantity]]}


def hire_action() -> dict:
    return {"farmer": ["PASS"], "hands": [], "market": [["HIRE"]]}


def buy_land_action() -> dict:
    return {"farmer": ["PASS"], "hands": [], "market": [["BUY_LAND"]]}


def movement_action(direction: str = "NORTH") -> dict:
    return {"farmer": [direction], "hands": [], "market": []}


def build_coop_action() -> dict:
    return {"farmer": ["BUILD_COOP"], "hands": [], "market": []}


def build_pasture_action() -> dict:
    return {"farmer": ["BUILD_PASTURE"], "hands": [], "market": []}


def feed_action() -> dict:
    return {"farmer": ["FEED"], "hands": [], "market": []}


def care_action() -> dict:
    return {"farmer": ["CARE"], "hands": [], "market": []}


def collect_fertilizer_action() -> dict:
    return {"farmer": ["COLLECT_FERTILIZER"], "hands": [], "market": []}


def pickup_action(item: str = "WHEAT", quantity: int = 1) -> dict:
    return {"farmer": ["PICKUP", item, quantity], "hands": [], "market": []}


def drop_action() -> dict:
    return {"farmer": ["DROP"], "hands": [], "market": []}


def place_action(item: str = "WHEAT") -> dict:
    return {"farmer": ["PLACE", item], "hands": [], "market": []}
