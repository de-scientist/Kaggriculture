"""Unit tests for the Tile domain model (chapter 9)."""

from __future__ import annotations

from agent.domain.animal import Animal
from agent.domain.crop import Crop
from agent.domain.position import Position
from agent.domain.tile import Tile


class TestTileConstruction:
    def test_defaults(self) -> None:
        tile = Tile(position=Position(0, 0))
        assert tile.terrain == "PLAIN"
        assert tile.crop is None
        assert tile.animal is None
        assert tile.fertility == 1.0
        assert tile.moisture == 0.0

    def test_custom_terrain(self) -> None:
        tile = Tile(position=Position(1, 2), terrain="WATER")
        assert tile.terrain == "WATER"
        assert tile.is_walkable is False

    def test_water_terrain_not_walkable(self) -> None:
        tile = Tile(position=Position(0, 0), terrain="WATER")
        assert tile.is_walkable is False

    def test_grass_terrain_walkable(self) -> None:
        tile = Tile(position=Position(0, 0), terrain="GRASS")
        assert tile.is_walkable is True


class TestTileOccupancy:
    def test_empty_tile(self) -> None:
        tile = Tile(position=Position(0, 0))
        assert tile.is_empty is True
        assert tile.is_occupied is False

    def test_tile_with_crop(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=0)
        tile = Tile(position=Position(0, 0), crop=crop)
        assert tile.is_empty is False
        assert tile.is_occupied is True
        assert tile.is_buildable is False

    def test_tile_with_animal(self) -> None:
        tile = Tile(position=Position(0, 0), animal=Animal(animal_type="GOOSE"))
        assert tile.is_empty is False
        assert tile.is_occupied is True

    def test_empty_plain_tile_is_buildable(self) -> None:
        tile = Tile(position=Position(0, 0), terrain="PLAIN")
        assert tile.is_buildable is True

    def test_empty_grass_tile_is_buildable(self) -> None:
        tile = Tile(position=Position(0, 0), terrain="GRASS")
        assert tile.is_buildable is True

    def test_water_tile_not_buildable(self) -> None:
        tile = Tile(position=Position(0, 0), terrain="WATER")
        assert tile.is_buildable is False


class TestTileBuilders:
    def test_with_crop_replaces_existing(self) -> None:
        crop1 = Crop(crop_type="WHEAT", planted_day=0)
        crop2 = Crop(crop_type="CARROT", planted_day=1)
        tile = Tile(position=Position(0, 0), crop=crop1)
        new_tile = tile.with_crop(crop2)
        assert new_tile.crop is crop2
        assert new_tile.crop is not crop1

    def test_with_animal_replaces_existing(self) -> None:
        animal1 = Animal(animal_type="GOOSE")
        animal2 = Animal(animal_type="COW")
        tile = Tile(position=Position(0, 0), animal=animal1)
        new_tile = tile.with_animal(animal2)
        assert new_tile.animal is animal2

    def test_remove_crop(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=0)
        tile = Tile(position=Position(0, 0), crop=crop)
        empty = tile.remove_crop()
        assert empty.crop is None

    def test_remove_animal(self) -> None:
        tile = Tile(position=Position(0, 0), animal=Animal(animal_type="GOOSE"))
        empty = tile.remove_animal()
        assert empty.animal is None

    def test_update_moisture(self) -> None:
        tile = Tile(position=Position(0, 0))
        updated = tile.update_moisture(0.5)
        assert updated.moisture == 0.5
        assert tile.moisture == 0.0

    def test_repr_contains_position(self) -> None:
        tile = Tile(position=Position(3, 4))
        assert "3" in repr(tile) or "4" in repr(tile)
