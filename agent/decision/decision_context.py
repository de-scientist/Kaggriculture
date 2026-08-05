from dataclasses import dataclass, field
from typing import Any


@dataclass
class DecisionContext:
    obs: dict
    player: int
    game_state: Any = None
    config: dict = field(default_factory=dict)