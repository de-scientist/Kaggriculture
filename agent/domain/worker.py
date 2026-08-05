from dataclasses import dataclass, field


@dataclass
class Worker:
    position: list = field(default_factory=list)
    inventory: dict = field(default_factory=dict)
    busy: bool = False
