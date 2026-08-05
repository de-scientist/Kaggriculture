from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StrategyContext:
    game_state: Any = None
    step: int = 0
    day: int = 0
    remaining_turns: int = 720
    market_snapshot: dict = field(default_factory=dict)
    config: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)