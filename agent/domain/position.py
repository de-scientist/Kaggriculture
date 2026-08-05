from __future__ import annotations


class Position:
    __slots__ = ("_x", "_y")

    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def distance_to(self, other: Position) -> int:
        return abs(self._x - other._x) + abs(self._y - other._y)

    def neighbors(self) -> list[Position]:
        return [
            Position(self._x, self._y - 1),
            Position(self._x, self._y + 1),
            Position(self._x - 1, self._y),
            Position(self._x + 1, self._y),
        ]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return False
        return self._x == other._x and self._y == other._y

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __repr__(self) -> str:
        return f"Position(x={self._x}, y={self._y})"