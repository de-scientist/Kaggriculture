"""Stage 2 — Land Investment Optimizer.

Evaluates land expansion investments based on expected return.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LandInvestment:
    """A land expansion investment recommendation."""

    quadrant: str
    cost: float
    expected_additional_profit: float
    payback_turns: float
    roi: float
    remaining_turns: int
    can_afford: bool
    confidence: float
    reason: str

    @property
    def is_viable(self) -> bool:
        return self.can_afford and self.payback_turns <= self.remaining_turns

    @property
    def strategic_value(self) -> float:
        if self.payback_turns <= 0:
            return 0.0
        return self.expected_additional_profit / self.payback_turns


@dataclass
class LandOptimizer:
    """Evaluates land expansion investments."""

    land_costs: dict[str, int] = field(
        default_factory=lambda: {"NE": 1000, "SW": 2000, "SE": 4000}
    )
    unlock_order: list[str] = field(default_factory=lambda: ["NE", "SW", "SE"])
    min_roi_threshold: float = 10.0  # minimum 10% ROI

    def evaluate_expansion(
        self,
        available_cash: float,
        unlocked_quadrants: list[str],
        remaining_turns: int,
        farm_profit_per_turn: float,
        tile_count: int = 0,
    ) -> list[LandInvestment]:
        """Evaluate all available land expansion opportunities."""
        recommendations: list[LandInvestment] = []

        for quadrant in self.unlock_order:
            if quadrant in unlocked_quadrants:
                continue

            cost = float(self.land_costs.get(quadrant, 5000))
            if cost > available_cash * 0.5:  # Only consider if affordable
                continue

            additional_tiles = 25  # 5x5 quadrant
            expected_profit = farm_profit_per_turn * additional_tiles / max(1, tile_count + 1)

            if expected_profit <= 0:
                continue

            payback = cost / expected_profit if expected_profit > 0 else float("inf")
            roi = (expected_profit * remaining_turns - cost) / cost * 100.0
            can_afford = available_cash >= cost
            confidence = min(1.0, tile_count / max(1, tile_count + 25))

            rec = LandInvestment(
                quadrant=quadrant,
                cost=cost,
                expected_additional_profit=expected_profit,
                payback_turns=payback,
                roi=roi,
                remaining_turns=remaining_turns,
                can_afford=can_afford,
                confidence=confidence,
                reason=f"Unlock {quadrant} for ${cost:.0f}, "
                f"ROI={roi:.1f}%, payback={payback:.1f} turns",
            )

            if rec.is_viable and roi >= self.min_roi_threshold:
                recommendations.append(rec)

        return sorted(recommendations, key=lambda r: (-r.strategic_value, r.quadrant))

    def next_best(
        self,
        available_cash: float,
        unlocked_quadrants: list[str],
        remaining_turns: int,
        farm_profit_per_turn: float,
        tile_count: int = 0,
    ) -> LandInvestment | None:
        recs = self.evaluate_expansion(
            available_cash=available_cash,
            unlocked_quadrants=unlocked_quadrants,
            remaining_turns=remaining_turns,
            farm_profit_per_turn=farm_profit_per_turn,
            tile_count=tile_count,
        )
        return recs[0] if recs else None
