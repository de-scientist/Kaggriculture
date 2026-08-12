"""Shared farm fixtures for Kaggriculture tests."""

from __future__ import annotations

from agent.domain.crop import Crop
from agent.domain.farm import Farm
from agent.domain.position import Position
from agent.domain.tile import Tile
from agent.domain.worker import Worker


def empty_farm(money: float = 3000.0) -> Farm:
    return Farm(
        tiles={},
        quadrants=["NW"],
        buildings=[],
        workers=[Worker(worker_id="farmer", position=Position(0, 0))],
        money=money,
    )


def farm_with_quadrants(*quadrants: str, money: float = 3000.0) -> Farm:
    return Farm(
        tiles={},
        quadrants=list(quadrants) if quadrants else ["NW"],
        buildings=[],
        workers=[Worker(worker_id="farmer", position=Position(0, 0))],
        money=money,
    )


def farm_with_crops(crops: list[tuple[int, int, str, int]], money: float = 3000.0) -> Farm:
    farm = empty_farm(money)
    for x, y, crop_type, planted_day in crops:
        pos = Position(x, y)
        crop = Crop(crop_type=crop_type, planted_day=planted_day)
        tile = Tile(position=pos).with_crop(crop)
        farm = farm.set_tile(pos, tile)
    return farm


def farm_with_workers(n_workers: int, money: float = 3000.0) -> Farm:
    workers = [Worker(worker_id=f"worker_{i}", position=Position(0, i)) for i in range(n_workers)]
    return Farm(
        tiles={},
        quadrants=["NW"],
        buildings=[],
        workers=workers,
        money=money,
    )


def farm_with_buildings(buildings: list[str], money: float = 3000.0) -> Farm:
    return Farm(
        tiles={},
        quadrants=["NW"],
        buildings=list(buildings),
        workers=[Worker(worker_id="farmer", position=Position(0, 0))],
        money=money,
    )


def farm_poor() -> Farm:
    return empty_farm(money=50.0)


def farm_affluent() -> Farm:
    return empty_farm(money=10000.0)
