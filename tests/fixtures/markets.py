"""Shared market fixtures for Kaggriculture tests."""
from __future__ import annotations

from agent.domain.market import Market


def empty_market() -> Market:
    return Market()


def market_with_prices(prices: dict[str, int]) -> Market:
    return Market(prices=dict(prices))


def market_with_inventory(inventory: dict[str, int]) -> Market:
    return Market(inventory=dict(inventory))


def market_full(prices: dict[str, int], inventory: dict[str, int]) -> Market:
    return Market(inventory=dict(inventory), prices=dict(prices))


def wheat_market() -> Market:
    return Market(
        inventory={"WHEAT": 10000, "CARROT": 10000, "TOMATO": 10000},
        prices={"WHEAT": 25, "CARROT": 35, "TOMATO": 45},
    )


def stratified_market() -> Market:
    return Market(
        inventory={"WHEAT": 10000, "STRAWBERRY": 5000, "MELON": 2000, "MILK": 1000, "WHEAT": 100},
        prices={"WHEAT": 25, "STRAWBERRY": 75, "MELON": 100, "MILK": 50},
    )
