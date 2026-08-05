from dataclasses import dataclass, field


@dataclass
class MarketState:
    inventory: dict[str, int] = field(default_factory=dict)
    prices: dict[str, int] = field(default_factory=dict)
