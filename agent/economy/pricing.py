def calculate_price(base: float, inventory: int, i0: int, shape: str) -> int:
    diff = inventory - i0
    if shape == "linear":
        price = base * (1 - 0.01 * diff)
    elif shape == "sq":
        price = base * (1 - 0.0001 * diff * diff)
    elif shape == "sqrt":
        price = base * (1 - 0.05 * (diff**0.5 if diff > 0 else -((-diff) ** 0.5)))
    elif shape == "log":
        import math

        price = base * (1 - 0.1 * math.log1p(abs(diff)) * (1 if diff >= 0 else -1))
    else:
        price = base
    return max(1, int(price))
