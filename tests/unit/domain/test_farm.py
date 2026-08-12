"""Unit tests for the Farm domain model (chapter 9)."""

from __future__ import annotations

import pytest

from agent.domain.farm import Farm
from agent.domain.position import Position
from agent.domain.tile import Tile
from agent.domain.worker import Worker


class TestFarmConstruction:
    def test_defaults(self) -> None:
        farm = Farm()
        assert farm.money == 3000.0
        assert farm.quadrants == []
        assert farm.buildings == []
        assert farm.workers == []
        assert farm.tiles == {}

    def test_custom_values(self) -> None:
        pos = Position(0, 0)
        tile = Tile(position=pos)
        farm = Farm(
            tiles={pos: tile},
            quadrants=["NW"],
            buildings=["COOP"],
            workers=[Worker(worker_id="farmer", position=pos)],
            money=5000.0,
        )
        assert farm.money == 5000.0
        assert farm.quadrants == ["NW"]
        assert farm.buildings == ["COOP"]
        assert len(farm.workers) == 1
        assert farm.tile_at(pos) is tile


class TestFarmTiles:
    def test_set_tile(self) -> None:
        farm = Farm()
        pos = Position(0, 0)
        tile = Tile(position=pos)
        new_farm = farm.set_tile(pos, tile)
        assert new_farm.tile_at(pos) is tile
        assert farm.tile_at(pos) is None

    def test_empty_tiles(self) -> None:
        pos = Position(0, 0)
        farm = Farm(tiles={pos: Tile(position=pos)})
        assert farm.empty_tiles() == []

    def test_empty_tiles_mixed(self) -> None:
        occupied = Position(0, 0)
        empty = Position(1, 0)
        farm = Farm(
            tiles={
                occupied: Tile(position=occupied),
                empty: None,
            }
        )
        result = farm.empty_tiles()
        assert Position(1, 0) in result

    def test_occupied_tiles(self) -> None:
        pos = Position(0, 0)
        farm = Farm(tiles={pos: Tile(position=pos)})
        assert pos in farm.occupied_tiles()

    def test_find_nearest_empty(self) -> None:
        farm = Farm(
            tiles={
                Position(0, 0): Tile(position=Position(0, 0)),
                Position(2, 0): None,
                Position(0, 3): None,
            }
        )
        nearest = farm.find_nearest_empty(Position(1, 0))
        assert nearest == Position(2, 0)

    def test_find_nearest_empty_none(self) -> None:
        farm = Farm(tiles={Position(0, 0): Tile(position=Position(0, 0))})
        assert farm.find_nearest_empty(Position(0, 0)) is None


class TestFarmQuadrants:
    def test_add_quadrant(self) -> None:
        farm = Farm(quadrants=["NW"])
        new_farm = farm.add_quadrant("NE")
        assert "NE" in new_farm.quadrants
        assert "NE" not in farm.quadrants

    def test_add_duplicate_quadrant_raises(self) -> None:
        farm = Farm(quadrants=["NW"])
        with pytest.raises(ValueError, match="already unlocked"):
            farm.add_quadrant("NW")


class TestFarmBuildings:
    def test_add_building(self) -> None:
        farm = Farm()
        new_farm = farm.add_building("COOP")
        assert "COOP" in new_farm.buildings

    def test_add_building_does_not_mutate_original(self) -> None:
        farm = Farm()
        farm.add_building("COOP")
        assert farm.buildings == []


class TestFarmWorkers:
    def test_add_worker(self) -> None:
        farm = Farm()
        worker = Worker(worker_id="farmer", position=Position(0, 0))
        new_farm = farm.add_worker(worker)
        assert len(new_farm.workers) == 1

    def test_remove_worker(self) -> None:
        worker = Worker(worker_id="farmer", position=Position(0, 0))
        farm = Farm(workers=[worker])
        new_farm = farm.remove_worker("farmer")
        assert len(new_farm.workers) == 0
        assert len(farm.workers) == 1


class TestFarmEconomy:
    def test_spend(self) -> None:
        farm = Farm(money=1000.0)
        new_farm = farm.spend(500.0)
        assert new_farm.money == 500.0

    def test_spend_insufficient_raises(self) -> None:
        farm = Farm(money=100.0)
        with pytest.raises(ValueError, match="Insufficient funds"):
            farm.spend(500.0)

    def test_earn(self) -> None:
        farm = Farm(money=1000.0)
        new_farm = farm.earn(500.0)
        assert new_farm.money == 1500.0


class TestFarmRepr:
    def test_repr_contains_key_fields(self) -> None:
        farm = Farm(money=5000.0, quadrants=["NW"])
        r = repr(farm)
        assert "money=5000" in r
        assert "NW" in r
