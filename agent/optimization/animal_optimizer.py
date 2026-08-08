"""Stage 2 — Animal Production Pipeline Optimizer.

Evaluates animal investment decisions based on profitability, payback
period, and ongoing production requirements.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent.economics.profit_model import (
    ANIMAL_PARAMS,
    ProfitabilityEstimate,
    estimate_animal_profitability,
)


@dataclass(frozen=True)
class AnimalRecommendation:
    """A recommendation for animal investment or management."""

    animal_type: str
    action: str  # "buy", "feed", "care", "collect", "skip"
    priority: int
    score: float
    profitability: ProfitabilityEstimate
    reason: str
    confidence: float


@dataclass
class AnimalOptimizer:
    """Evaluates animal investment opportunities."""

    base_prices: dict[str, int] = field(
        default_factory=lambda: {"EGG": 30, "MILK": 50, "WOOL": 40, "FERTILIZER": 15}
    )
    feed_cost_per_day: float = 10.0  # wheat seed cost

    def evaluate_purchase(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_cash: float,
        existing_animals: dict[str, int],
        has_structure: dict[str, bool],
    ) -> list[AnimalRecommendation]:
        """Evaluate all available animal purchase opportunities."""
        recommendations: list[AnimalRecommendation] = []

        for animal_type, params in ANIMAL_PARAMS.items():
            purchase_cost = params["purchase_cost"]
            if purchase_cost > available_cash:
                continue

            structure = params["structure"]
            if not has_structure.get(structure, False):
                continue

            product = params["product"]
            sale_price = market_prices.get(product, self.base_prices.get(product, 30))

            profitability = estimate_animal_profitability(
                animal_type=animal_type,
                current_day=current_day,
                remaining_turns=remaining_turns,
                sale_price=sale_price,
            )

            if profitability.expected_profit <= 0:
                continue

            existing_count = existing_animals.get(animal_type, 0)
            diversification_bonus = 1.0 if existing_count == 0 else 0.85
            adjusted_score = profitability.profit_per_turn * profitability.roi * diversification_bonus

            recommendations.append(
                AnimalRecommendation(
                    animal_type=animal_type,
                    action="buy",
                    priority=len(recommendations),
                    score=adjusted_score,
                    profitability=profitability,
                    reason=f"Buy {animal_type}: ROI={profitability.roi:.1f}%, "
                    f"profit/turn={profitability.profit_per_turn:.1f}",
                    confidence=min(1.0, remaining_turns / max(1, profitability.growth_duration + 10)),
                )
            )

        recommendations.sort(key=lambda r: (-r.score, r.animal_type))
        for i, rec in enumerate(recommendations):
            rec = AnimalRecommendation(
                animal_type=rec.animal_type,
                action=rec.action,
                priority=i,
                score=rec.score,
                profitability=rec.profitability,
                reason=rec.reason,
                confidence=rec.confidence,
            )
            recommendations[i] = rec

        return recommendations

    def best_purchase(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_cash: float,
        existing_animals: dict[str, int],
        has_structure: dict[str, bool],
    ) -> AnimalRecommendation | None:
        recs = self.evaluate_purchase(
            current_day=current_day,
            remaining_turns=remaining_turns,
            market_prices=market_prices,
            available_cash=available_cash,
            existing_animals=existing_animals,
            has_structure=has_structure,
        )
        return recs[0] if recs else None
