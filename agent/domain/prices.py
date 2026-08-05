from dataclasses import dataclass


@dataclass
class PriceInfo:
    base: float = 0.0
    shape_below: str = "linear"
    shape_above: str = "linear"
    current: int = 0
    inventory: int = 0
