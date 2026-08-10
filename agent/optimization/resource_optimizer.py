from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Bottleneck:
    name: str
    severity: float
    current_value: float = 0.0
    capacity: float = 0.0
    recommendation: str = ""


class ResourceOptimizer:
    """Optimizes scarce resources: cash, land, workers, inventory capacity,
    animal capacity, and time.

    Identifies bottlenecks and recommends upgrades.
    """

    CASH_FLOOR = 500.0
    SHED_UTILIZATION_THRESHOLD = 0.9
    LAND_UTILIZATION_THRESHOLD = 0.9
    ANIMAL_UTILIZATION_THRESHOLD = 0.9
    EARLY_GAME_THRESHOLD = 5
    LATE_GAME_THRESHOLD = 100
    ENDGAME_THRESHOLD = 30

    def __init__(self):
        self._bottlenecks: dict[str, float] = {}
        self._resource_data: dict[str, Any] = {}

    def is_early_game(self, value: int) -> bool:
        return value < self.EARLY_GAME_THRESHOLD

    def is_late_game(self, value: int) -> bool:
        return value <= self.LATE_GAME_THRESHOLD

    def is_endgame(self, value: int) -> bool:
        return value <= self.ENDGAME_THRESHOLD

    def identify_bottlenecks(
        self,
        cash: float,
        workers: int,
        land_tiles: int,
        land_capacity: int,
        shed_items: int,
        shed_capacity: int,
        animal_count: int,
        animal_capacity: int,
        remaining_turns: int,
    ) -> list[Bottleneck]:
        bottlenecks: list[Bottleneck] = []

        if cash < self.CASH_FLOOR:
            severity = max(0.0, min(1.0, (self.CASH_FLOOR - cash) / self.CASH_FLOOR))
            bottlenecks.append(
                Bottleneck(
                    name="cash",
                    severity=severity,
                    current_value=cash,
                    capacity=self.CASH_FLOOR,
                    recommendation="Delay large purchases; prioritize selling produce.",
                )
            )

        if workers < 1:
            bottlenecks.append(
                Bottleneck(
                    name="workers",
                    severity=0.9,
                    current_value=float(workers),
                    capacity=1.0,
                    recommendation="Hire a farm hand to increase throughput.",
                )
            )

        if land_capacity > 0 and land_tiles / land_capacity > self.LAND_UTILIZATION_THRESHOLD:
            ratio = land_tiles / land_capacity
            bottlenecks.append(
                Bottleneck(
                    name="land",
                    severity=ratio,
                    current_value=float(land_tiles),
                    capacity=float(land_capacity),
                    recommendation="Buy additional land to expand planting capacity.",
                )
            )

        if shed_capacity > 0 and shed_items / shed_capacity > self.SHED_UTILIZATION_THRESHOLD:
            ratio = shed_items / shed_capacity
            bottlenecks.append(
                Bottleneck(
                    name="shed_capacity",
                    severity=ratio,
                    current_value=float(shed_items),
                    capacity=float(shed_capacity),
                    recommendation="Sell produce to free shed capacity.",
                )
            )

        if animal_capacity > 0 and animal_count / animal_capacity > self.ANIMAL_UTILIZATION_THRESHOLD:
            ratio = animal_count / animal_capacity
            bottlenecks.append(
                Bottleneck(
                    name="animal_capacity",
                    severity=ratio,
                    current_value=float(animal_count),
                    capacity=float(animal_capacity),
                    recommendation="Build more coops or pastures to hold more animals.",
                )
            )

        if self.is_endgame(remaining_turns):
            bottlenecks.append(
                Bottleneck(
                    name="time",
                    severity=1.0,
                    current_value=float(remaining_turns),
                    capacity=float(self.ENDGAME_THRESHOLD),
                    recommendation="Liquidate inventory; stop long-term investments.",
                )
            )

        bottlenecks.sort(key=lambda b: (-b.severity, b.name))
        self._bottlenecks = {b.name: b.severity for b in bottlenecks}
        return bottlenecks

    def primary_bottleneck(
        self,
        cash: float,
        workers: int,
        land_tiles: int,
        land_capacity: int,
        shed_items: int,
        shed_capacity: int,
        animal_count: int,
        animal_capacity: int,
        remaining_turns: int,
    ) -> Bottleneck | None:
        bottlenecks = self.identify_bottlenecks(
            cash=cash,
            workers=workers,
            land_tiles=land_tiles,
            land_capacity=land_capacity,
            shed_items=shed_items,
            shed_capacity=shed_capacity,
            animal_count=animal_count,
            animal_capacity=animal_capacity,
            remaining_turns=remaining_turns,
        )
        return bottlenecks[0] if bottlenecks else None

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
