"""Shared observation fixtures for Kaggriculture tests.

Each function returns a fresh copy of a canonical observation dict so that
tests never mutate shared state.  Fixtures mirror the observation schema
documented in the Kaggle environment README.
"""
from __future__ import annotations

from copy import deepcopy

_TILE_NW = [
    [None] * 10,
    [None] * 10,
    [None] * 10,
    [None] * 10,
    [None] * 10,
]


def minimal_observation() -> dict:
    return {
        "player": 0,
        "step": 0,
        "day": 0,
        "hour": 0,
        "remaining_turns": 720,
        "farms": [_empty_farm(), _empty_farm()],
        "private": {"shed": {}, "seeds": {}, "inventories": [{}]},
        "market": {"inventory": {}, "prices": {}},
        "town": {"unlocked_shops": []},
    }


def _empty_farm() -> dict:
    return {
        "money": 3000.0,
        "tiles": [[None for _ in range(10)] for _ in range(10)],
        "farmer": [0, 0],
        "hands": [],
        "unlocked_quadrants": ["NW"],
        "hires_today": 0,
    }


def observation_with_crop(crop: str = "WHEAT", planted_day: int = 0) -> dict:
    obs = minimal_observation()
    farm = deepcopy(obs["farms"][0])
    y, x = 0, 0
    farm["tiles"][y][x] = {
        "kind": "PLANT",
        "crop": crop,
        "planted_day": planted_day,
        "watered_today": False,
        "consecutive_unwatered": 0,
        "yield_units": 0,
        "max_lifespan_step": 10,
        "fertilized_until_day": -1,
    }
    obs["farms"][0] = farm
    return obs


def observation_with_money(money: float) -> dict:
    obs = minimal_observation()
    obs["farms"][0]["money"] = money
    obs["farms"][1]["money"] = 5000.0
    return obs


def observation_with_seeds(seeds: dict[str, int]) -> dict:
    obs = minimal_observation()
    obs["private"]["seeds"] = dict(seeds)
    return obs


def observation_with_shed(shed: dict[str, int]) -> dict:
    obs = minimal_observation()
    obs["private"]["shed"] = dict(shed)
    return obs


def observation_with_hands(n_hands: int) -> dict:
    obs = minimal_observation()
    hands = [[x, 0] for x in range(1, n_hands + 1)]
    obs["farms"][0]["hands"] = hands
    obs["farms"][0]["hires_today"] = n_hands
    return obs


def observation_with_animal(animal_type: str = "GOOSE") -> dict:
    obs = minimal_observation()
    farm = deepcopy(obs["farms"][0])
    y, x = 0, 5
    farm["tiles"][y][x] = {
        "kind": "COOP",
        "animal": {"animal_type": animal_type, "fed_today": False},
        "placed_day": 0,
        "yield_units": 0,
        "fed_today": False,
        "consecutive_unfed": 0,
        "cared_today": False,
        "fertilizer_available": False,
        "pending_care_bonus": 0,
    }
    obs["farms"][0] = farm
    return obs


def observation_with_market(prices: dict[str, int], inventory: dict[str, int] | None = None) -> dict:
    obs = minimal_observation()
    obs["market"] = {"inventory": dict(inventory or {}), "prices": dict(prices)}
    return obs


def observation_with_town(shops: list[str]) -> dict:
    obs = minimal_observation()
    obs["town"] = {"unlocked_shops": list(shops)}
    return obs


def observation_with_quadrant(quadrant: str = "NE") -> dict:
    obs = minimal_observation()
    obs["farms"][0]["unlocked_quadrants"] = ["NW", quadrant]
    return obs


def observation_malformed() -> dict:
    return {"player": 0}


def observation_partial() -> dict:
    return {
        "player": 0,
        "step": 0,
        "farms": [{"money": 3000}],
        "private": {},
        "market": {},
        "town": {},
    }


def observation_advanced(day: int = 5, money: float = 4500.0) -> dict:
    obs = minimal_observation()
    obs["day"] = day
    obs["step"] = day * 24
    obs["farms"][0]["money"] = money
    obs["farms"][0]["unlocked_quadrants"] = ["NW", "NE", "SW"]
    return obs
