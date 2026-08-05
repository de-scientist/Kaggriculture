from dataclasses import dataclass, field
from typing import Dict


@dataclass
class MarketState:
    inventory: Dict[str, int] = field(default_factory=dict)
    prices: Dict[str, int] = field(default_factory=dict)