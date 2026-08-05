from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Inventory:
    items: Dict[str, int] = field(default_factory=dict)
    capacity: int = 100