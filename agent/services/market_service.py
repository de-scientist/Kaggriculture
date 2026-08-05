from agent.domain.market import Market
from agent.domain.prices import Price


def get_price(market: Market, product: str) -> Price:
    return market.current_price(product)


def update_price(market: Market, product: str, new_price: int) -> Market:
    return market.update_price(product, new_price)


def update_inventory(market: Market, product: str, delta: int) -> Market:
    return market.update_inventory(product, delta)


def estimate_roi(
    market: Market, product: str, cost: float, expected_price: float
) -> float:
    return market.estimate_roi(product, cost, expected_price)
