from agent.economy import roi
from agent.economy import pricing


def evaluate_investment(cost: float, expected_return: float, risk: float = 0.0) -> float:
    return roi.calculate_roi(cost, expected_return) * (1 - risk)


def compute_price(base: float, inventory: int, i0: int, shape: str) -> int:
    return pricing.calculate_price(base, inventory, i0, shape)