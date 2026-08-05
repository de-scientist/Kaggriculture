def should_invest(cash: float, cost: float, min_reserve: float) -> bool:
    return cash - cost >= min_reserve
