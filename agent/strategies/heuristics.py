from __future__ import annotations


def estimate_profit(estimated_reward: float, estimated_cost: float) -> float:
    return estimated_reward - estimated_cost


def growth_urgency(age: int, max_lifespan: int) -> float:
    if max_lifespan <= 0:
        return 0.0
    return age / max_lifespan


def hunger_urgency(consecutive_unfed: int) -> float:
    return min(1.0, consecutive_unfed / 2.0)


def market_attractiveness(price: int, base_price: int) -> float:
    if base_price <= 0:
        return 0.0
    return price / base_price


def inventory_pressure(current: int, capacity: int) -> float:
    if capacity <= 0:
        return 0.0
    return current / capacity


def worker_utilization(available: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return available / total


def expansion_readiness(utilization: float) -> float:
    return max(0.0, utilization - 0.7)