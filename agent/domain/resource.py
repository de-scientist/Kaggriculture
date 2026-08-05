from __future__ import annotations


class Resource:
    __slots__ = ("_name", "_amount")

    def __init__(self, name: str, amount: int) -> None:
        self._name = name
        self._amount = amount

    @property
    def name(self) -> str:
        return self._name

    @property
    def amount(self) -> int:
        return self._amount

    def add(self, quantity: int) -> Resource:
        if quantity < 0:
            raise ValueError("Cannot add negative quantity")
        return Resource(self._name, self._amount + quantity)

    def subtract(self, quantity: int) -> Resource:
        if quantity < 0:
            raise ValueError("Cannot subtract negative quantity")
        new_amount = self._amount - quantity
        if new_amount < 0:
            raise ValueError(f"Insufficient {self._name}: need {quantity}, have {self._amount}")
        return Resource(self._name, new_amount)

    def validate(self, required: int) -> bool:
        return self._amount >= required

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Resource):
            return False
        return self._name == other._name and self._amount == other._amount

    def __repr__(self) -> str:
        return f"Resource(name={self._name!r}, amount={self._amount})"