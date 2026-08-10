from __future__ import annotations

from typing import Any


def parse_player(obs: dict[str, Any]) -> int:
    return int(obs["player"])


def parse_farm_layout(obs: dict[str, Any]) -> list[list[Any]]:
    player = int(obs["player"])
    tiles = obs["farms"][player]["tiles"]
    return [[tile for tile in row] for row in tiles]


def parse_worker_positions(obs: dict[str, Any]) -> dict[str, list[Any]]:
    player = int(obs["player"])
    farm = obs["farms"][player]
    return {
        "farmer": farm.get("farmer", [0, 0]),
        "hands": farm.get("hands", []),
    }


def parse_inventory(obs: dict[str, Any]) -> dict[str, Any]:
    return dict(obs["private"].get("shed", {}))


def parse_seeds(obs: dict[str, Any]) -> dict[str, Any]:
    return dict(obs["private"].get("seeds", {}))


def parse_market(obs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "inventory": dict(obs["market"].get("inventory", {})),
        "prices": dict(obs["market"].get("prices", {})),
    }


def parse_town(obs: dict[str, Any]) -> dict[str, list[Any]]:
    return {
        "unlocked_shops": list(obs["town"].get("unlocked_shops", [])),
    }


def parse_season(obs: dict[str, Any]) -> dict[str, int]:
    return {
        "day": int(obs["day"]),
        "hour": int(obs["hour"]),
        "step": int(obs["step"]),
    }


def parse_crops(obs: dict[str, Any]) -> list[dict[str, Any]]:
    tiles = parse_farm_layout(obs)
    crops: list[dict[str, Any]] = []
    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                crops.append(
                    {
                        "position": [x, y],
                        "crop_type": tile.get("crop", ""),
                        "planted_day": tile.get("planted_day", -1),
                        "watered_today": tile.get("watered_today", False),
                        "consecutive_unwatered": tile.get("consecutive_unwatered", 0),
                        "yield_units": tile.get("yield_units", 0),
                        "max_lifespan_step": tile.get("max_lifespan_step", 0),
                        "fertilized_until_day": tile.get("fertilized_until_day", -1),
                    }
                )
    return crops


def parse_animals(obs: dict[str, Any]) -> list[dict[str, Any]]:
    tiles = parse_farm_layout(obs)
    animals: list[dict[str, Any]] = []
    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE"):
                animal_data = tile.get("animal")
                if animal_data is not None:
                    animals.append(
                        {
                            "position": [x, y],
                            "animal_type": animal_data.get("animal", ""),
                            "housing": tile.get("kind", ""),
                            "placed_day": tile.get("placed_day", -1),
                            "yield_units": tile.get("yield_units", 0),
                            "fed_today": tile.get("fed_today", False),
                            "consecutive_unfed": tile.get("consecutive_unfed", 0),
                            "cared_today": tile.get("cared_today", False),
                            "fertilizer_available": tile.get("fertilizer_available", False),
                            "pending_care_bonus": tile.get("pending_care_bonus", 0),
                        }
                    )
    return animals
