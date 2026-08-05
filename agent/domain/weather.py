from __future__ import annotations


class Weather:
    __slots__ = ("_condition", "_rainy", "_windy")

    def __init__(self, condition: str = "clear", rainy: bool = False, windy: bool = False) -> None:
        self._condition = condition
        self._rainy = rainy
        self._windy = windy

    @property
    def condition(self) -> str:
        return self._condition

    @property
    def rainy(self) -> bool:
        return self._rainy

    @property
    def windy(self) -> bool:
        return self._windy

    def __repr__(self) -> str:
        return f"Weather(condition={self._condition!r}, rainy={self._rainy}, windy={self._windy})"
