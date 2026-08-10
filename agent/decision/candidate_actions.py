from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CandidateAction:
    id: str
    action_type: str
    target_entity: str = ""
    target_position: tuple[int, int] | None = None
    worker: str = ""
    estimated_cost: float = 0.0
    estimated_reward: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    strategy_annotations: dict[str, Any] = field(default_factory=dict)

    @property
    def net_value(self) -> float:
        return self.estimated_reward - self.estimated_cost
