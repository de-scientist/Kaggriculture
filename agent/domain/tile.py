from __future__ import annotations

from agent.domain.position import Position


class Tile:
    __slots__ = ("_position", "_terrain", "_crop", "_animal", "_fertility", "_moisture", "_owner")

    def __init__(
        self,
        position: Position,
        terrain: str = "PLAIN",
        crop: object | None = None,
        animal: object | None = None,
        fertility: float = 1.0,
        moisture: float = 0.0,
        owner: int = 0,
    ) -> None:
        self._position = position
        self._terrain = terrain
        self._crop = crop
        self._animal = animal
        self._fertility = fertility
        self._moisture = moisture
        self._owner = owner

    @property
    def position(self) -> Position:
        return self._position

    @property
    def terrain(self) -> str:
        return self._terrain

    @property
    def crop(self) -> object | None:
        return self._crop

    @property
    def animal(self) -> object | None:
        return self._animal

    @property
    def fertility(self) -> float:
        return self._fertility

    @property
    def moisture(self) -> float:
        return self._moisture

    @property
    def owner(self) -> int:
        return self._owner

    @property
    def is_empty(self) -> bool:
        return self._crop is None and self._animal is None

    @property
    def is_occupied(self) -> bool:
        return self._crop is not None or self._animal is not None

    @property
    def is_walkable(self) -> bool:
        return self._terrain != "WATER"

    @property
    def is_buildable(self) -> bool:
        return self.is_empty and self._terrain in ("PLAIN", "GRASS")

    def with_crop(self, crop: object) -> Tile:
        if self._crop is not None:
            raise ValueError(f"Tile {self._position} already has a crop")
        return Tile(
            position=self._position,
            terrain=self._terrain,
            crop=crop,
            animal=self._animal,
            fertility=self._fertility,
            moisture=self._moisture,
            owner=self._owner,
        )

    def with_animal(self, animal: object) -> Tile:
        if self._animal is not None:
            raise ValueError(f"Tile {self._position} already has an animal")
        return Tile(
            position=self._position,
            terrain=self._terrain,
            crop=self._crop,
            animal=animal,
            fertility=self._fertility,
            moisture=self._moisture,
            owner=self._owner,
        )

    def remove_crop(self) -> Tile:
        return Tile(
            position=self._position,
            terrain=self._terrain,
            crop=None,
            animal=self._animal,
            fertility=self._fertility,
            moisture=self._moisture,
            owner=self._owner,
        )

    def remove_animal(self) -> Tile:
        return Tile(
            position=self._position,
            terrain=self._terrain,
            crop=self._crop,
            animal=None,
            fertility=self._fertility,
            moisture=self._moisture,
            owner=self._owner,
        )

    def update_moisture(self, moisture: float) -> Tile:
        return Tile(
            position=self._position,
            terrain=self._terrain,
            crop=self._crop,
            animal=self._animal,
            fertility=self._fertility,
            moisture=moisture,
            owner=self._owner,
        )

    def __repr__(self) -> str:
        return f"Tile(pos={self._position}, terrain={self._terrain!r}, crop={self._crop is not None}, animal={self._animal is not None})"