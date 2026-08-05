def calculate_roi(cost: float, expected_return: float) -> float:
    if cost == 0:
        return 0.0
    return (expected_return - cost) / cost