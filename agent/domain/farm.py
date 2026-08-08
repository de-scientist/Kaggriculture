from __future__ import annotations

from agent.domain.position import Position
from agent.domain.worker import Worker


class Farm:
    __slots__ = ("_buildings", "_money", "_quadrants", "_tiles", "_workers")

    def __init__(
        self,
        tiles: dict[Position, object] | None = None,
        quadrants: list[str] | None = None,
        buildings: list[str] | None = None,
        workers: list[object] | None = None,
        money: float = 3000.0,
    ) -> None:
        self._tiles = dict(tiles or {})
        self._quadrants = list(quadrants or [])
        self._buildings = list(buildings or [])
        self._workers = list(workers or [Worker(worker_id="farmer", position=Position(0, 0))])
        self._money = money

    @property
    def tiles(self) -> dict[Position, object]:
        return dict(self._tiles)

    @property
    def quadrants(self) -> list[str]:
        return list(self._quadrants)

    @property
    def buildings(self) -> list[str]:
        return list(self._buildings)

    @property
    def workers(self) -> list[object]:
        return list(self._workers)

    @property
    def money(self) -> float:
        return self._money

    def tile_at(self, position: Position) -> object | None:
        return self._tiles.get(position)

    def set_tile(self, position: Position, tile: object) -> Farm:
        new_tiles = dict(self._tiles)
        new_tiles[position] = tile
        return Farm(
            tiles=new_tiles,
            quadrants=self._quadrants,
            buildings=self._buildings,
            workers=self._workers,
            money=self._money,
        )

    def add_quadrant(self, quadrant: str) -> Farm:
        if quadrant in self._quadrants:
            raise ValueError(f"Quadrant {quadrant} already unlocked")
        new_quadrants = list(self._quadrants)
        new_quadrants.append(quadrant)
        return Farm(
            tiles=self._tiles,
            quadrants=new_quadrants,
            buildings=self._buildings,
            workers=self._workers,
            money=self._money,
        )

    def add_building(self, building: str) -> Farm:
        new_buildings = list(self._buildings)
        new_buildings.append(building)
        return Farm(
            tiles=self._tiles,
            quadrants=self._quadrants,
            buildings=new_buildings,
            workers=self._workers,
            money=self._money,
        )

    def add_worker(self, worker: object) -> Farm:
        new_workers = list(self._workers)
        new_workers.append(worker)
        return Farm(
            tiles=self._tiles,
            quadrants=self._quadrants,
            buildings=self._buildings,
            workers=new_workers,
            money=self._money,
        )

    def remove_worker(self, worker_id: str) -> Farm:
        new_workers = [w for w in self._workers if getattr(w, "id", None) != worker_id]
        return Farm(
            tiles=self._tiles,
            quadrants=self._quadrants,
            buildings=self._buildings,
            workers=new_workers,
            money=self._money,
        )

    def spend(self, amount: float) -> Farm:
        if amount > self._money:
            raise ValueError(f"Insufficient funds: need {amount}, have {self._money}")
        return Farm(
            tiles=self._tiles,
            quadrants=self._quadrants,
            buildings=self._buildings,
            workers=self._workers,
            money=self._money - amount,
        )

    def earn(self, amount: float) -> Farm:
        return Farm(
            tiles=self._tiles,
            quadrants=self._quadrants,
            buildings=self._buildings,
            workers=self._workers,
            money=self._money + amount,
        )

    def empty_tiles(self) -> list[Position]:
        return [pos for pos, tile in self._tiles.items() if tile is None]

    def occupied_tiles(self) -> list[Position]:
        return [pos for pos, tile in self._tiles.items() if tile is not None]

    def find_nearest_empty(self, from_pos: Position) -> Position | None:
        empty = self.empty_tiles()
        if not empty:
            return None
        return min(empty, key=lambda p: p.distance_to(from_pos))

    def __repr__(self) -> str:
        return (
            f"Farm(money={self._money}, tiles={len(self._tiles)}, "
            f"quadrants={self._quadrants}, workers={len(self._workers)})"
        )
