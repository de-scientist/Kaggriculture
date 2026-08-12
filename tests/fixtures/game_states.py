"""Shared game-state builder fixtures.

These factory functions produce :class:`~agent.domain.game_state.GameState`
instances for use across unit and integration tests.
"""

from __future__ import annotations

from typing import cast

from agent.domain.animal import Animal
from agent.domain.crop import Crop
from agent.domain.farm import Farm
from agent.domain.game_state import GameState
from agent.domain.inventory import Inventory
from agent.domain.market import Market
from agent.domain.position import Position
from agent.domain.season import Season
from agent.domain.tile import Tile
from agent.domain.worker import Worker


def empty_game_state(player: int = 0) -> GameState:
    farm = Farm(
        tiles={},
        quadrants=["NW"],
        buildings=[],
        workers=[Worker(worker_id="farmer", position=Position(0, 0))],
        money=3000.0,
    )
    return GameState(
        player=player,
        farm=farm,
        inventory=Inventory(),
        market=Market(),
        step=0,
    )


def game_state_with_money(player: int = 0, money: float = 5000.0) -> GameState:
    state = empty_game_state(player)
    return GameState(
        player=player,
        farm=state.farm.spend(state.farm.money - money) if state.farm.money > money else state.farm,
        inventory=state.inventory,
        market=state.market,
        step=state.step,
    )


def game_state_with_crop(crop_type: str = "WHEAT", planted_day: int = 0) -> GameState:
    state = empty_game_state()
    pos = Position(0, 0)
    crop = Crop(crop_type=crop_type, planted_day=planted_day)
    tile = Tile(position=pos).with_crop(crop)
    farm = state.farm.set_tile(pos, tile)
    return GameState(
        player=state.player,
        farm=farm,
        inventory=state.inventory,
        market=state.market,
        step=state.step,
    )


def game_state_with_mature_crop(crop_type: str = "WHEAT", planted_day: int = 0) -> GameState:
    state = game_state_with_crop(crop_type, planted_day)
    pos = Position(0, 0)
    tile = cast(Tile, state.farm.tile_at(pos))
    crop = cast(Crop, tile.crop)
    mature_tile = tile.with_crop(crop)
    farm = state.farm.set_tile(pos, mature_tile)
    return GameState(
        player=state.player,
        farm=farm,
        inventory=state.inventory,
        market=state.market,
        step=state.step,
    )


def game_state_with_animal(animal_type: str = "GOOSE", fed: bool = False) -> GameState:
    state = empty_game_state()
    animal = Animal(animal_type=animal_type)
    if fed:
        animal = animal.feed()
    pos = Position(0, 5)
    tile = Tile(position=pos).with_animal(animal)
    farm = state.farm.set_tile(pos, tile)
    return GameState(
        player=state.player,
        farm=farm,
        inventory=state.inventory,
        market=state.market,
        step=state.step,
    )


def game_state_with_inventory(items: dict[str, int]) -> GameState:
    state = empty_game_state()
    inventory = Inventory()
    for item, qty in items.items():
        inventory = inventory.add(item, qty)
    return GameState(
        player=state.player,
        farm=state.farm,
        inventory=inventory,
        market=state.market,
        step=state.step,
    )


def game_state_with_market(
    prices: dict[str, int], inventory: dict[str, int] | None = None
) -> GameState:
    state = empty_game_state()
    market = Market(
        inventory=dict(inventory or {}),
        prices=dict(prices),
    )
    return GameState(
        player=state.player,
        farm=state.farm,
        inventory=state.inventory,
        market=market,
        step=state.step,
    )


def game_state_advanced(day: int = 5, money: float = 4500.0) -> GameState:
    state = empty_game_state()
    season = Season(day=day, turn=0, turns_per_day=24, total_days=30, total_turns=720)
    farm = Farm(
        tiles={},
        quadrants=["NW", "NE", "SW"],
        buildings=["COOP"],
        workers=[Worker(worker_id="farmer", position=Position(0, 0))],
        money=money,
    )
    return GameState(
        player=state.player,
        farm=farm,
        inventory=state.inventory,
        market=state.market,
        season=season,
        step=day * 24,
    )
