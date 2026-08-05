from __future__ import annotations

from dataclasses import dataclass

from agent.domain.market import Market
from agent.domain.prices import Price


@dataclass(frozen=True)
class MarketSnapshot:
    prices: dict[str, int]
    inventory: dict[str, int]
    turn: int

    @classmethod
    def from_market(cls, market: Market, turn: int) -> MarketSnapshot:
        return cls(
            prices=dict(market.prices),
            inventory=dict(market.inventory),
            turn=turn,
        )


def buy_price(market: Market, product: str) -> Price:
    return market.current_price(product)


def sell_price(market: Market, product: str) -> Price:
    return market.current_price(product)


def current_prices(market: Market) -> dict[str, int]:
    return dict(market.prices)


def price_history(market: Market) -> list[dict[str, int]]:
    return list(market.history)


def best_sell_option(market: Market, products: list[str]) -> tuple[str, Price] | None:
    best_product = None
    best_price = Price(value=0)
    for product in products:
        price = market.current_price(product)
        if price > best_price:
            best_price = price
            best_product = product
    if best_product is None:
        return None
    return best_product, best_price


def best_buy_option(market: Market, products: list[str]) -> tuple[str, Price] | None:
    best_product = None
    best_price = Price(value=float("inf"))
    for product in products:
        price = market.current_price(product)
        if price < best_price:
            best_price = price
            best_product = product
    if best_product is None:
        return None
    return best_product, best_price
