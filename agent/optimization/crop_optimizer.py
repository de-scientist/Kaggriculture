"""Stage 2 — Crop Portfolio Optimizer.

Evaluates crop planting decisions based on profitability, timing, and
portfolio diversification. Uses only information available at the
current turn.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent.economics.profit_model import (
    CROP_PARAMS,
    ProfitabilityEstimate,
    estimate_crop_profitability,
)


@dataclass(frozen=True)
class CropRecommendation:
    """A recommendation for crop planting or management."""

    crop_type: str
    action: str  # "plant", "water", "harvest", "fertilize", "skip"
    priority: int
    score: float
    profitability: ProfitabilityEstimate
    reason: str
    confidence: float


@dataclass
class CropOptimizer:
    """Evaluates crop opportunities and produces recommendations.

    All evaluations use the current day, remaining turns, and observed
    market prices. No future information is used.
    """

    base_prices: dict[str, int] = field(
        default_factory=lambda: {
            "WHEAT": 10,
            "CARROT": 20,
            "TOMATO": 25,
            "STRAWBERRY": 50,
            "MELON": 80,
        }
    )

    def evaluate_planting(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_seeds: dict[str, int],
        available_cash: float,
        planted_tiles: dict[str, int],
    ) -> list[CropRecommendation]:
        """Evaluate all available planting opportunities."""
        recommendations: list[CropRecommendation] = []

        for crop_type, params in CROP_PARAMS.items():
            seed_cost = params["seed_cost"]
            if seed_cost > available_cash:
                continue
            if available_seeds.get(crop_type, 0) <= 0:
                continue

            first_yield = params.get("first_yield_day", 2)
            max_yield = params.get("max_yield_day", 10)
            growth_duration = max_yield - current_day

            if growth_duration <= 0:
                continue

            if growth_duration > remaining_turns:
                continue

            sale_price = market_prices.get(crop_type, self.base_prices.get(crop_type, 10))
            profitability = estimate_crop_profitability(
                crop_type=crop_type,
                current_day=current_day,
                remaining_turns=remaining_turns,
                sale_price=sale_price,
            )

            if profitability.expected_profit <= 0:
                continue

            existing = planted_tiles.get(crop_type, 0)
            diversity_bonus = 1.0 if existing == 0 else 0.9
            adjusted_score = profitability.profit_per_turn * profitability.roi * diversity_bonus

            recommendations.append(
                CropRecommendation(
                    crop_type=crop_type,
                    action="plant",
                    priority=len(recommendations),
                    score=adjusted_score,
                    profitability=profitability,
                    reason=f"Plant {crop_type}: ROI={profitability.roi:.1f}%, "
                    f"profit/turn={profitability.profit_per_turn:.1f}",
                    confidence=min(1.0, growth_duration / max(1, params.get("max_yield_day", 10))),
                )
            )

        recommendations.sort(key=lambda r: (-r.score, r.crop_type))
        for i, rec in enumerate(recommendations):
            rec = CropRecommendation(
                crop_type=rec.crop_type,
                action=rec.action,
                priority=i,
                score=rec.score,
                profitability=rec.profitability,
                reason=rec.reason,
                confidence=rec.confidence,
            )
            recommendations[i] = rec

        return recommendations

    def optimal_crop(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_seeds: dict[str, int],
        available_cash: float,
        planted_tiles: dict[str, int],
    ) -> CropRecommendation | None:
        """Return the single highest-value planting recommendation."""
        recs = self.evaluate_planting(
            current_day=current_day,
            remaining_turns=remaining_turns,
            market_prices=market_prices,
            available_seeds=available_seeds,
            available_cash=available_cash,
            planted_tiles=planted_tiles,
        )
        return recs[0] if recs else None

    def portfolio(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_seeds: dict[str, int],
        available_cash: float,
        max_plantings: int = 5,
    ) -> list[CropRecommendation]:
        """Return a diversified set of planting recommendations."""
        all_recs = self.evaluate_planting(
            current_day=current_day,
            remaining_turns=remaining_turns,
            market_prices=market_prices,
            available_seeds=available_seeds,
            available_cash=available_cash,
            planted_tiles={},
        )

        portfolio: list[CropRecommendation] = []
        used_cash = 0.0
        for rec in all_recs:
            if len(portfolio) >= max_plantings:
                break
            if used_cash + rec.profitability.seed_cost > available_cash:
                continue
            portfolio.append(rec)
            used_cash += rec.profitability.seed_cost

        return portfolio
