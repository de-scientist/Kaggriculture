from __future__ import annotations

import time

from agent.adapters import validators
from agent.adapters.compatibility import normalize_observation
from agent.domain import game_state as gs_domain
from agent.domain.farm import Farm
from agent.domain.inventory import Inventory
from agent.domain.market import Market
from agent.domain.position import Position
from agent.domain.season import Season
from agent.domain.tile import Tile
from agent.domain.town import Town
from agent.utilities.logging import get_logger

logger = get_logger("agent.adapters.observation")


class ObservationAdapter:
    def parse(self, obs: dict) -> gs_domain.GameState:
        start = time.perf_counter()
        logger.info(
            "Parsing observation for player %s at step %s",
            obs.get("player"),
            obs.get("step"),
        )

        validators.validate_observation_not_none(obs)
        validators.validate_observation_schema(obs)
        normalize_observation(obs)

        player = obs["player"]
        farm_data = obs["farms"][player]

        inventory = Inventory()
        private = obs.get("private", {})
        for item, count in private.get("shed", {}).items():
            try:
                inventory = inventory.add(item, count)
            except ValueError:
                pass

        farm = Farm(
            money=farm_data.get("money", 3000.0),
            quadrants=farm_data.get("unlocked_quadrants", ["NW"]),
        )
        for y, row in enumerate(farm_data.get("tiles", [])):
            for x, tile_data in enumerate(row):
                pos = Position(x, y)
                if tile_data is None:
                    tile = Tile(position=pos)
                elif isinstance(tile_data, dict):
                    tile = Tile(position=pos, terrain="PLAIN")
                else:
                    tile = Tile(position=pos)
                farm = farm.set_tile(pos, tile)

        market_data = obs.get("market", {})
        market = Market(
            inventory=market_data.get("inventory", {}),
            prices=market_data.get("prices", {}),
        )

        town_data = obs.get("town", {})
        town = Town(unlocked_shops=town_data.get("unlocked_shops", []))

        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        season = Season(day=day, turn=hour)
        game_state = gs_domain.GameState(
            player=player,
            farm=farm,
            inventory=inventory,
            market=market,
            town=town,
            season=season,
            private=private,
            step=obs.get("step", 0),
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("Observation parsed in %.2f ms", elapsed_ms)
        return game_state

    def _build_tiles(self, obs: dict) -> dict:
        tiles: dict = {}
        player = obs["player"]
        farm_data = obs["farms"][player]
        for y, row in enumerate(farm_data.get("tiles", [])):
            for x, tile_data in enumerate(row):
                pos = Position(x, y)
                if tile_data is None:
                    tiles[pos] = None
                elif isinstance(tile_data, dict):
                    tiles[pos] = tile_data
                else:
                    tiles[pos] = None
        return tiles
