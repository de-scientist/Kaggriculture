from __future__ import annotations


class Statistics:
    __slots__ = (
        "_animals_produced",
        "_coins_earned",
        "_coins_spent",
        "_crops_harvested",
        "_land_purchased",
    )

    def __init__(
        self,
        crops_harvested: int = 0,
        animals_produced: int = 0,
        land_purchased: int = 0,
        coins_earned: float = 0.0,
        coins_spent: float = 0.0,
    ) -> None:
        self._crops_harvested = crops_harvested
        self._animals_produced = animals_produced
        self._land_purchased = land_purchased
        self._coins_earned = coins_earned
        self._coins_spent = coins_spent

    @property
    def crops_harvested(self) -> int:
        return self._crops_harvested

    @property
    def animals_produced(self) -> int:
        return self._animals_produced

    @property
    def land_purchased(self) -> int:
        return self._land_purchased

    @property
    def coins_earned(self) -> float:
        return self._coins_earned

    @property
    def coins_spent(self) -> float:
        return self._coins_spent

    def record_harvest(self) -> Statistics:
        return Statistics(
            crops_harvested=self._crops_harvested + 1,
            animals_produced=self._animals_produced,
            land_purchased=self._land_purchased,
            coins_earned=self._coins_earned,
            coins_spent=self._coins_spent,
        )

    def record_land_purchase(self) -> Statistics:
        return Statistics(
            crops_harvested=self._crops_harvested,
            animals_produced=self._animals_produced,
            land_purchased=self._land_purchased + 1,
            coins_earned=self._coins_earned,
            coins_spent=self._coins_spent,
        )

    def record_earnings(self, amount: float) -> Statistics:
        return Statistics(
            crops_harvested=self._crops_harvested,
            animals_produced=self._animals_produced,
            land_purchased=self._land_purchased,
            coins_earned=self._coins_earned + amount,
            coins_spent=self._coins_spent,
        )

    def record_expense(self, amount: float) -> Statistics:
        return Statistics(
            crops_harvested=self._crops_harvested,
            animals_produced=self._animals_produced,
            land_purchased=self._land_purchased,
            coins_earned=self._coins_earned,
            coins_spent=self._coins_spent + amount,
        )

    def total_wealth(self, wallet_balance: float) -> float:
        return wallet_balance + self._coins_earned - self._coins_spent

    def __repr__(self) -> str:
        return (
            f"Statistics(crops={self._crops_harvested}, animals={self._animals_produced}, "
            f"land={self._land_purchased}, earned={self._coins_earned}, spent={self._coins_spent})"
        )
