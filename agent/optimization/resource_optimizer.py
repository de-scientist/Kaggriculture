from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Bottleneck:
    resource: str
    current_value: int
    capacity: int
    constraint_score: float
    upgrade_cost: float
    upgrade_value: float


class ResourceOptimizer:
    """Optimizes scarce resources: cash, land, workers, water, fertilizer, feed, inventory capacity, production capacity.

    Identifies bottlenecks and recommends upgrades.
    """

    def __init__(self):
        self._bottlenecks: dict[str, float] = {}
        self._resource_data = {}

    def identify_bottleneck(
        self,
        current_state: Any,
        available_resources: dict[str, int],
    ) -> str | None:
        bottleneck = None
        max_bottleneck = 0
        for resource, capacity in available_resources.items():
            if capacity < 10:
                bottleneck = resource
                max_bottleneck = capacity
                break
        return bottleneck

    def evaluate_resource(
        self,
        resource: str,
        current_value: float,
        available_turns: int,
    ) -> Any:
        return None

    def set_resource_data(self, resource: str, data: dict) -> None:
        self._resource_data[resource] = data