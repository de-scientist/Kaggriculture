from dataclasses import dataclass, field


@dataclass
class Inventory:
    items: dict[str, int] = field(default_factory=dict)
    capacity: int = 100
