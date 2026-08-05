def process_orders(orders: list, player_id: int) -> list:
    return []


def get_price(market: dict, product: str) -> int:
    return market.get("prices", {}).get(product, 1)


def update_inventory(market: dict, product: str, delta: int) -> None:
    inv = market.get("inventory", {})
    inv[product] = inv.get(product, 0) + delta
    market["inventory"] = inv
