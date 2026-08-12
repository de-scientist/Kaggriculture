"""Typed, dependency-free view over a kaggriculture observation.

The engine hands every agent a dict observation (``obs``).  ``GameSnapshot``
normalizes that dict into convenient accessors used by the planner, the market
layer, and the learning feature builder.  Nothing here mutates engine state.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .constants import (
    ANIMAL_PRODUCTS,
    BOARD_SIZE_DEFAULT,
    CROPS,
    EPISODE_STEPS_DEFAULT,
    MARKET,
    SHED_CAPACITY,
    TURNS_PER_DAY_DEFAULT,
    window_start_day,
)

Position = tuple[int, int]

SHED_ACCESS: list[Position] = [(4, 4), (5, 4), (4, 5), (5, 5)]


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _get_mapping(data: Mapping[str, Any] | Any, key: str) -> Mapping[str, Any]:
    if isinstance(data, Mapping):
        value = data.get(key)
        if isinstance(value, Mapping):
            return value
    else:
        value = getattr(data, key, None)
        if isinstance(value, Mapping):
            return value
    return {}


@dataclass(frozen=True)
class GameSnapshot:
    """Immutable convenience wrapper over one observation."""

    obs: Mapping[str, Any]
    player: int
    step: int
    day: int
    hour: int
    turns_per_day: int
    episode_steps: int
    board_size: int
    farms: Sequence[Mapping[str, Any]]
    market: Mapping[str, Any]
    town: Mapping[str, Any]
    private: Mapping[str, Any]

    @classmethod
    def from_obs(cls, obs: Mapping[str, Any]) -> GameSnapshot:
        if isinstance(obs, Mapping):
            farms_raw = obs.get("farms", [])
            step_raw = obs.get("step", 0)
            day_raw = obs.get("day", 0)
            hour_raw = obs.get("hour", 0)
            player_raw = obs.get("player", 0)
            market = _get_mapping(obs, "market")
            town = _get_mapping(obs, "town")
            private = _get_mapping(obs, "private")
        else:
            farms_raw = getattr(obs, "farms", [])
            step_raw = getattr(obs, "step", 0)
            day_raw = getattr(obs, "day", 0)
            hour_raw = getattr(obs, "hour", 0)
            player_raw = getattr(obs, "player", 0)
            market = _get_mapping(obs, "market")
            town = _get_mapping(obs, "town")
            private = _get_mapping(obs, "private")
        farms: Sequence[Mapping[str, Any]] = (
            [f for f in farms_raw if isinstance(f, Mapping)] if isinstance(farms_raw, list) else []
        )
        player = _as_int(player_raw, 0)
        step = _as_int(step_raw, 0)
        day = _as_int(day_raw, 0)
        hour = _as_int(hour_raw, 0)
        if isinstance(obs, Mapping):
            tpd = _as_int(obs.get("turnsPerDay", TURNS_PER_DAY_DEFAULT), TURNS_PER_DAY_DEFAULT)
            steps = _as_int(obs.get("episodeSteps", EPISODE_STEPS_DEFAULT), EPISODE_STEPS_DEFAULT)
            board = _as_int(obs.get("boardSize", BOARD_SIZE_DEFAULT), BOARD_SIZE_DEFAULT)
        else:
            tpd = TURNS_PER_DAY_DEFAULT
            steps = EPISODE_STEPS_DEFAULT
            board = BOARD_SIZE_DEFAULT
        return cls(
            obs=obs,
            player=player,
            step=step,
            day=day,
            hour=hour,
            turns_per_day=tpd,
            episode_steps=steps,
            board_size=board,
            farms=farms,
            market=market,
            town=town,
            private=private,
        )

    # -- players ---------------------------------------------------------
    def me(self) -> Mapping[str, Any]:
        if 0 <= self.player < len(self.farms):
            return self.farms[self.player]
        return {}

    def opp(self) -> Mapping[str, Any]:
        other = 1 - self.player
        if 0 <= other < len(self.farms):
            return self.farms[other]
        return {}

    def money(self) -> float:
        return float(self.me().get("money", 0.0))

    def opp_money(self) -> float:
        return float(self.opp().get("money", 0.0))

    def money_diff(self) -> float:
        return self.money() - self.opp_money()

    # -- positions -------------------------------------------------------
    def farmer_pos(self) -> Position:
        farmer = self.me().get("farmer", [0, 0])
        try:
            return (int(farmer[0]), int(farmer[1]))
        except (TypeError, ValueError, IndexError):
            return (0, 0)

    def hands(self) -> list[Position]:
        raw = self.me().get("hands", [])
        out: list[Position] = []
        for pos in raw if isinstance(raw, list) else []:
            try:
                out.append((int(pos[0]), int(pos[1])))
            except (TypeError, ValueError, IndexError):
                continue
        return out

    def units(self) -> list[Position]:
        return [self.farmer_pos(), *self.hands()]

    # -- ownership / tiles ----------------------------------------------
    def unlocked(self) -> set[str]:
        raw = self.me().get("unlocked_quadrants", [])
        return set(str(q) for q in raw) if isinstance(raw, list) else set()

    def unlocked_count(self) -> int:
        return len(self.unlocked())

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def is_unlocked(self, x: int, y: int) -> bool:
        return (
            self.in_bounds(x, y)
            and self.tile_at(x, y) is not None
            and self.tile_at(x, y) != "LOCKED"
        )

    def tile_at(self, x: int, y: int) -> Any:
        if not self.in_bounds(x, y):
            return "LOCKED"
        tiles = self.me().get("tiles")
        if not isinstance(tiles, list):
            return "LOCKED"
        try:
            return tiles[y][x]
        except (IndexError, TypeError):
            return "LOCKED"

    def opp_tile_at(self, x: int, y: int) -> Any:
        if not self.in_bounds(x, y):
            return "LOCKED"
        tiles = self.opp().get("tiles")
        if not isinstance(tiles, list):
            return "LOCKED"
        try:
            return tiles[y][x]
        except (IndexError, TypeError):
            return "LOCKED"

    def count_tiles(self, kind: str) -> int:
        return self._count_kind(self.me(), kind)

    def opp_count_tiles(self, kind: str) -> int:
        return self._count_kind(self.opp(), kind)

    @staticmethod
    def _count_kind(farm: Mapping[str, Any], kind: str) -> int:
        tiles = farm.get("tiles")
        if not isinstance(tiles, list):
            return 0
        n = 0
        for row in tiles:
            if not isinstance(row, list):
                continue
            for tile in row:
                if tile is None and kind == "EMPTY":
                    n += 1
                elif tile == "LOCKED" and kind == "LOCKED":
                    n += 1
                elif isinstance(tile, dict):
                    if tile.get("kind") == kind:
                        n += 1
                    elif kind == "ANIMAL" and "animal" in tile:
                        n += 1
        return n

    def own_tile_count(self) -> int:
        return self.board_size * self.board_size - self.count_tiles("LOCKED")

    def empty_tiles(self) -> list[Position]:
        out: list[Position] = []
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.tile_at(x, y) is None:
                    out.append((x, y))
        return out

    def weed_tiles(self) -> list[Position]:
        out: list[Position] = []
        for y in range(self.board_size):
            for x in range(self.board_size):
                tile = self.tile_at(x, y)
                if isinstance(tile, dict) and tile.get("kind") == "WEED":
                    out.append((x, y))
        return out

    # -- shed / seeds / inventory ---------------------------------------
    def shed(self) -> Mapping[str, Any]:
        shed = self.private.get("shed", {})
        return shed if isinstance(shed, Mapping) else {}

    def shed_occupancy(self) -> int:
        return int(sum(int(v) for v in self.shed().values() if isinstance(v, (int, float))))

    def shed_value(self) -> float:
        prices = self.prices()
        return sum(
            float(v) * float(prices.get(k, 0.0))
            for k, v in self.shed().items()
            if isinstance(v, (int, float))
        )

    def seeds(self) -> Mapping[str, Any]:
        seeds = self.private.get("seeds", {})
        return seeds if isinstance(seeds, Mapping) else {}

    def seed_count(self, crop: str) -> int:
        return int(self.seeds().get(crop, 0))

    def inventories(self) -> list[Mapping[str, Any]]:
        raw = self.private.get("inventories", [])
        return [i for i in raw if isinstance(i, Mapping)] if isinstance(raw, list) else []

    def inventory_value(self, index: int = 0) -> float:
        inv = self.inventories()[index] if index < len(self.inventories()) else {}
        prices = self.prices()
        return sum(
            float(v) * float(prices.get(k, 0.0))
            for k, v in inv.items()
            if isinstance(v, (int, float))
        )

    def carrying(self, index: int, item: str) -> int:
        inv = self.inventories()[index] if index < len(self.inventories()) else {}
        return int(inv.get(item, 0))

    # -- market / town ---------------------------------------------------
    def prices(self) -> Mapping[str, Any]:
        return self.market.get("prices", {})

    def price(self, product: str) -> float:
        value = self.prices().get(product, MARKET.get(product, {}).get("base", 0))
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def market_inventory(self) -> Mapping[str, Any]:
        return self.market.get("inventory", {})

    def market_level(self, product: str) -> float:
        value = self.market_inventory().get(product, 0)
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def shops(self) -> list[str]:
        raw = self.town.get("unlocked_shops", [])
        return [str(s) for s in raw] if isinstance(raw, list) else []

    # -- season ----------------------------------------------------------
    def remaining_turns(self) -> int:
        return max(0, self.episode_steps - self.step)

    def remaining_days(self) -> int:
        return max(0, self.episode_steps // self.turns_per_day - self.day)

    def days_left(self) -> int:
        return max(0, (self.episode_steps - self.step) // self.turns_per_day)

    def season_days(self) -> int:
        return max(1, self.episode_steps // self.turns_per_day)

    def is_final_day(self) -> bool:
        return self.remaining_turns() <= self.turns_per_day

    # -- plant helpers ---------------------------------------------------
    @staticmethod
    def plant_age(tile: Mapping[str, Any], day: int) -> int:
        return day - int(tile.get("planted_day", 0))

    def in_window(self, tile: Mapping[str, Any]) -> bool:
        crop = str(tile.get("crop", ""))
        if crop not in CROPS or bool(CROPS[crop]["ongoing"]):
            return False
        age = self.plant_age(tile, self.day)
        return window_start_day(crop) <= age <= int(CROPS[crop]["max_yield_day"])

    def shed_adjacent(self, pos: Position) -> bool:
        return pos in {
            tile for tile in SHED_ACCESS if tile[0] < self.board_size and tile[1] < self.board_size
        }


def count_plants_by_crop(farm: Mapping[str, Any], crop: str) -> int:
    tiles = farm.get("tiles")
    if not isinstance(tiles, list):
        return 0
    n = 0
    for row in tiles:
        if not isinstance(row, list):
            continue
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == crop:
                n += 1
    return n


def product_is_animal_product(product: str) -> bool:
    return product in ANIMAL_PRODUCTS


def shed_capacity_used(snapshot: GameSnapshot) -> bool:
    return snapshot.shed_occupancy() >= SHED_CAPACITY - 1
