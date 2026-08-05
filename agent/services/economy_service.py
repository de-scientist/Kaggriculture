from __future__ import annotations


def roi(cost: float, revenue: float) -> float:
    if cost <= 0:
        return 0.0
    return (revenue - cost) / cost


def profit(revenue: float, cost: float) -> float:
    return revenue - cost


def cost(item: str, quantity: int, unit_cost: float) -> float:
    return unit_cost * quantity


def expected_return(item: str, quantity: int, unit_price: float) -> float:
    return unit_price * quantity


def payback_period(cost: float, daily_return: float) -> int:
    if daily_return <= 0:
        return -1
    import math

    return math.ceil(cost / daily_return)