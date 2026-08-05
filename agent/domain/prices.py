from __future__ import annotations


class Price:
    __slots__ = ("_currency", "_timestamp", "_value")

    def __init__(self, value: int, currency: str = "COIN", timestamp: int = 0) -> None:
        self._value = value
        self._currency = currency
        self._timestamp = timestamp

    @property
    def value(self) -> int:
        return self._value

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def timestamp(self) -> int:
        return self._timestamp

    def __lt__(self, other: Price) -> bool:
        return self._value < other._value

    def __le__(self, other: Price) -> bool:
        return self._value <= other._value

    def __gt__(self, other: Price) -> bool:
        return self._value > other._value

    def __ge__(self, other: Price) -> bool:
        return self._value >= other._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Price):
            return False
        return self._value == other._value

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __add__(self, other: int) -> Price:
        if not isinstance(other, int):
            return NotImplemented
        return Price(self._value + other, self._currency, self._timestamp)

    def __sub__(self, other: int) -> Price:
        if not isinstance(other, int):
            return NotImplemented
        return Price(max(0, self._value - other), self._currency, self._timestamp)

    def __mul__(self, other: float) -> Price:
        if not isinstance(other, (int, float)):
            return NotImplemented
        return Price(int(self._value * other), self._currency, self._timestamp)

    def pct_change(self, other: Price) -> float:
        if other._value == 0:
            return 0.0
        return (self._value - other._value) / other._value * 100

    def __repr__(self) -> str:
        return f"Price(value={self._value}, currency={self._currency!r})"
