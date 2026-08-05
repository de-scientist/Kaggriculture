from __future__ import annotations


class Wallet:
    __slots__ = ("_balance",)

    def __init__(self, balance: float = 0.0) -> None:
        if balance < 0:
            raise ValueError("Wallet balance cannot be negative")
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    def can_afford(self, cost: float) -> bool:
        return self._balance >= cost

    def deposit(self, amount: float) -> Wallet:
        if amount < 0:
            raise ValueError("Cannot deposit negative amount")
        return Wallet(self._balance + amount)

    def withdraw(self, amount: float) -> Wallet:
        if amount < 0:
            raise ValueError("Cannot withdraw negative amount")
        if amount > self._balance:
            raise ValueError(f"Insufficient funds: need {amount}, have {self._balance}")
        return Wallet(self._balance - amount)

    def __repr__(self) -> str:
        return f"Wallet(balance={self._balance})"
