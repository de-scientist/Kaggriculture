from dataclasses import dataclass, field
from typing import Any


@dataclass
class Worker:
    position: list = field(default_factory=list)
    inventory: dict = field(default_factory=dict)
    busy: bool = False