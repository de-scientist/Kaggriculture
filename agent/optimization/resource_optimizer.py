"""Stage 2 — Resource Optimization.

Identifies bottlenecks and recommends resource allocation priorities.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Bottleneck:
    """A resource constraint limiting production."""

    name: str
    severity: float  # 0.0 to 1.0 (1.0 = severely limiting)
    current: float
    capacity: float
    description: str


@dataclass
class ResourceOptimizer:
    """Identifies resource bottlenecks and recommends allocation."""

    def identify_bottlenecks(
        self,
        cash: float,
        workers: int,
        land_tiles: int,
        land_capacity: int = 100,
        shed_items: int = 0,
        shed_capacity: int = 100,
        animal_count: int = 0,
        animal_capacity: int = 0,
        remaining_turns: int = 720,
    ) -> list[Bottleneck]:
        """Identify the most binding resource constraints."""
        bottlenecks: list[Bottleneck] = []

        cash_severity = self._ratio_severity(cash, 500.0, 0.4)
        if cash_severity > 0.0:
            bottlenecks.append(
                Bottleneck(
                    name="cash",
                    severity=cash_severity,
                    current=cash,
                    capacity=500.0,
                    description="Low cash limits investment opportunities",
                )
            )

        land_severity = self._ratio_severity(land_tiles, land_capacity, 1.0)
        if land_severity > 0.0:
            bottlenecks.append(
                Bottleneck(
                    name="land",
                    severity=land_severity,
                    current=land_tiles,
                    capacity=land_capacity,
                    description=f"Limited land: {land_tiles}/{land_capacity} tiles used",
                )
            )

        worker_severity = self._ratio_severity(workers, max(1, workers), 0.0)
        if worker_severity > 0.0 and workers < 2:
            bottlenecks.append(
                Bottleneck(
                    name="workers",
                    severity=1.0 - (workers / 2.0),
                    current=workers,
                    capacity=2,
                    description=f"Only {workers} worker(s) available",
                )
            )

        shed_severity = self._ratio_severity(shed_items, shed_capacity, 0.9)
        if shed_severity > 0.0:
            bottlenecks.append(
                Bottleneck(
                    name="shed_capacity",
                    severity=shed_severity,
                    current=shed_items,
                    capacity=shed_capacity,
                    description="Shed near capacity — must sell soon",
                )
            )

        animal_severity = self._ratio_severity(animal_count, max(1, animal_capacity), 0.0)
        if animal_severity > 0.0 and animal_count < max(1, animal_capacity):
            underutilization = 1.0 - (animal_count / max(1, animal_capacity))
            if underutilization > 0.3:
                bottlenecks.append(
                    Bottleneck(
                        name="animal_capacity",
                        severity=underutilization,
                        current=animal_count,
                        capacity=max(1, animal_capacity),
                        description="Animal housing underutilized",
                    )
                )

        if remaining_turns < 50:
            bottlenecks.append(
                Bottleneck(
                    name="time",
                    severity=1.0 - (remaining_turns / 720.0),
                    current=remaining_turns,
                    capacity=720,
                    description=f"Only {remaining_turns} turns remaining — shift to liquidation",
                )
            )

        bottlenecks.sort(key=lambda b: (-b.severity, b.name))
        return bottlenecks

    def is_endgame(self, remaining_turns: int) -> bool:
        return remaining_turns < 50

    def is_late_game(self, remaining_turns: int) -> bool:
        return remaining_turns < 200

    def is_early_game(self, current_day: int) -> bool:
        return current_day < 5

    def _ratio_severity(self, current: float, capacity: float, threshold: float) -> float:
        if capacity <= 0:
            return 0.0
        ratio = current / capacity
        if ratio < threshold:
            return threshold - ratio
        return 0.0

    def primary_bottleneck(self, **kwargs: float) -> Bottleneck | None:
        bottlenecks = self.identify_bottlenecks(**kwargs)
        return bottlenecks[0] if bottlenecks else None

    def allocation_priorities(self, **kwargs: float) -> list[str]:
        bottlenecks = self.identify_bottlenecks(**kwargs)
        return [b.name for b in bottlenecks]
