from __future__ import annotations

from agent.domain.crop import Crop
from agent.domain.tile import Tile


def plant(tile: Tile, crop_type: str, day: int) -> Tile:
    if tile.crop is not None:
        raise ValueError(f"Cannot plant on occupied tile at {tile.position}")
    crop = Crop(crop_type=crop_type, planted_day=day)
    return tile.with_crop(crop)


def water(tile: Tile) -> Tile:
    if tile.crop is None:
        raise ValueError("Cannot water a tile with no crop")
    if tile.crop.is_harvested:
        raise ValueError("Cannot water a harvested crop")
    updated_crop = tile.crop.water()
    return tile.with_crop(updated_crop)


def fertilize(tile: Tile, day: int) -> Tile:
    if tile.crop is None:
        raise ValueError("Cannot fertilize a tile with no crop")
    updated_crop = tile.crop.fertilize(day)
    return tile.with_crop(updated_crop)


def harvest(tile: Tile, current_day: int = 0) -> Tile:
    if tile.crop is None:
        raise ValueError("Cannot harvest a tile with no crop")
    if not tile.crop.is_mature(current_day):
        raise ValueError("Cannot harvest an immature crop")
    updated_crop = tile.crop.harvest()
    return tile.with_crop(updated_crop)


def can_plant(tile: Tile) -> bool:
    return tile.crop is None


def can_harvest(tile: Tile, day: int) -> bool:
    return tile.crop is not None and tile.crop.is_mature(day)


def expected_profit(crop_type: str, day: int, sell_price: float, seed_cost: float) -> float:
    return sell_price - seed_cost


def growth_progress(tile: Tile, day: int) -> float:
    if tile.crop is None:
        return 0.0
    maturity_days = 2
    age = day - tile.crop.planted_day
    if age >= maturity_days:
        return 1.0
    return age / maturity_days


def ready_for_harvest(tile: Tile, day: int) -> bool:
    return can_harvest(tile, day)


def needs_water(tile: Tile) -> bool:
    if tile.crop is None:
        return False
    return not tile.crop.watered_today


def needs_fertilizer(tile: Tile, day: int) -> bool:
    if tile.crop is None:
        return False
    return tile.crop.fertilized_until_day < day


def empty_tiles(tiles: list[Tile]) -> list[Tile]:
    return [t for t in tiles if t.crop is None]


def highest_roi_crop(
    tiles: list[Tile],
    day: int,
    prices: dict[str, float],
    costs: dict[str, float],
) -> str | None:
    best = None
    best_roi = -1.0
    for t in tiles:
        if t.crop is None:
            continue
        crop_type = t.crop.crop_type
        roi = expected_profit(crop_type, day, prices.get(crop_type, 0.0), costs.get(crop_type, 0.0))
        if roi > best_roi:
            best_roi = roi
            best = crop_type
    return best
