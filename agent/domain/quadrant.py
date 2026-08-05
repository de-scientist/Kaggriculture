from __future__ import annotations


class Quadrant:
    __slots__ = ("_cost", "_name", "_owner", "_unlocked")

    def __init__(
        self,
        name: str = "NW",
        unlocked: bool = False,
        cost: int = 0,
        owner: int = 0,
    ) -> None:
        self._name = name
        self._unlocked = unlocked
        self._cost = cost
        self._owner = owner

    @property
    def name(self) -> str:
        return self._name

    @property
    def unlocked(self) -> bool:
        return self._unlocked

    @property
    def cost(self) -> int:
        return self._cost

    @property
    def owner(self) -> int:
        return self._owner

    def unlock(self, owner: int) -> Quadrant:
        return Quadrant(
            name=self._name,
            unlocked=True,
            cost=self._cost,
            owner=owner,
        )

    def __repr__(self) -> str:
        return f"Quadrant(name={self._name!r}, unlocked={self._unlocked}, cost={self._cost})"
