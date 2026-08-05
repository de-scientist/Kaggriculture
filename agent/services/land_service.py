from __future__ import annotations

from agent.domain.quadrant import Quadrant

QUADRANT_COSTS = {
    "NE": 1000,
    "SW": 2000,
    "SE": 4000,
}

QUADRANT_NEIGHBORS = {
    "NW": ["NE", "SW"],
    "NE": ["NW", "SE"],
    "SW": ["NW", "SE"],
    "SE": ["NE", "SW"],
}


def available_land(farm: object) -> list[str]:
    unlocked = getattr(farm, "quadrants", [])
    return [q for q in ["NE", "SW", "SE"] if q not in unlocked]


def purchase_cost(quadrant: str) -> int:
    return QUADrant_COSTS.get(quadrant, 0)


def expandable(farm: object, money: float) -> list[str]:
    available = available_land(farm)
    return [q for q in available if purchase_cost(q) <= money]


def neighboring_quadrants(quadrant: str) -> list[str]:
    return QUADrant_NEIGHBORS.get(quadrant, [])


def expected_land_value(quadrant: str) -> float:
    cost = purchase_cost(quadrant)
    if cost == 0:
        return 0.0
    return cost * 1.5