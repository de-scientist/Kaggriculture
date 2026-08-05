from __future__ import annotations


class Town:
    __slots__ = ("_demand", "_town_center_sell_interval", "_unlocked_shops")

    def __init__(
        self,
        unlocked_shops: list[str] | None = None,
        demand: dict[str, int] | None = None,
        town_center_sell_interval: int = 12,
    ) -> None:
        self._unlocked_shops = list(unlocked_shops or [])
        self._demand = dict(demand or {})
        self._town_center_sell_interval = town_center_sell_interval

    @property
    def unlocked_shops(self) -> list[str]:
        return list(self._unlocked_shops)

    @property
    def demand(self) -> dict[str, int]:
        return dict(self._demand)

    @property
    def town_center_sell_interval(self) -> int:
        return self._town_center_sell_interval

    def has_shop(self, shop_name: str) -> bool:
        return shop_name in self._unlocked_shops

    def get_demand(self, product: str) -> int:
        return self._demand.get(product, 0)

    def __repr__(self) -> str:
        return f"Town(shops={self._unlocked_shops}, demand={self._demand})"
