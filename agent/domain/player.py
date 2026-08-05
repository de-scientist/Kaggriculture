from __future__ import annotations

from agent.domain.farm import Farm
from agent.domain.inventory import Inventory
from agent.domain.statistics import Statistics
from agent.domain.wallet import Wallet


class Player:
    __slots__ = ("_index", "_wallet", "_farm", "_inventory", "_statistics")

    def __init__(
        self,
        index: int,
        wallet: Wallet | None = None,
        farm: Farm | None = None,
        inventory: Inventory | None = None,
        statistics: Statistics | None = None,
    ) -> None:
        self._index = index
        self._wallet = wallet or Wallet()
        self._farm = farm or Farm()
        self._inventory = inventory or Inventory()
        self._statistics = statistics or Statistics()

    @property
    def index(self) -> int:
        return self._index

    @property
    def wallet(self) -> Wallet:
        return self._wallet

    @property
    def farm(self) -> Farm:
        return self._farm

    @property
    def inventory(self) -> Inventory:
        return self._inventory

    @property
    def statistics(self) -> Statistics:
        return self._statistics

    @property
    def money(self) -> float:
        return self._wallet.balance

    def can_afford(self, cost: float) -> bool:
        return self._wallet.can_afford(cost)

    def spend(self, amount: float) -> Player:
        new_wallet = self._wallet.withdraw(amount)
        new_stats = self._statistics.record_expense(amount)
        return Player(
            index=self._index,
            wallet=new_wallet,
            farm=self._farm,
            inventory=self._inventory,
            statistics=new_stats,
        )

    def earn(self, amount: float) -> Player:
        new_wallet = self._wallet.deposit(amount)
        new_stats = self._statistics.record_earnings(amount)
        return Player(
            index=self._index,
            wallet=new_wallet,
            farm=self._farm,
            inventory=self._inventory,
            statistics=new_stats,
        )

    def total_wealth(self) -> float:
        return self._statistics.total_wealth(self._wallet.balance)

    def __repr__(self) -> str:
        return (
            f"Player(index={self._index}, money={self._wallet.balance}, "
            f"wealth={self.total_wealth()})"
        )