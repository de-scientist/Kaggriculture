from dataclasses import dataclass, field


@dataclass
class MarketSnapshot:
    timestamp: int = 0
    inventory: dict[str, int] = field(default_factory=dict)
    prices: dict[str, int] = field(default_factory=dict)
