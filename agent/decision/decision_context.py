from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DecisionContext:
    obs: dict
    player: int
    game_state: Any = None
    config: dict = field(default_factory=dict)
    step: int = 0
    day: int = 0
    hour: int = 0
    remaining_turns: int = 720
    strategy_name: str = "baseline"