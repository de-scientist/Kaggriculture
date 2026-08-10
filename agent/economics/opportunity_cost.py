"""Stage 2 — Opportunity Cost Engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OpportunityCost:
    """Represents the cost of choosing one resource use over another."""

    label: str
    cost: float
    description: str = ""


@dataclass
class OpportunityCostEngine:
    """Calculates opportunity costs for resource allocation decisions.

    All calculations use only information available at the current turn.
    """

    def worker_opportunity_cost(
        self,
        worker_id: str,
        current_action_value: float,
        alternative_actions: list[tuple[str, float]],
    ) -> OpportunityCost:
        best_alt_value = max((v for _, v in alternative_actions), default=0.0)
        cost = max(0.0, best_alt_value - current_action_value)
        return OpportunityCost(
            label=f"worker_{worker_id}",
            cost=cost,
            description=f"Foregone value from not choosing best alternative for worker {worker_id}",
        )

    def cash_opportunity_cost(
        self,
        amount: float,
        alternative_roi: float,
        remaining_turns: int,
    ) -> OpportunityCost:
        cost = amount * (alternative_roi / 100.0) * remaining_turns / 365.0
        return OpportunityCost(
            label="cash_allocation",
            cost=cost,
            description=f"Foregone return from not investing ${amount} at {alternative_roi}% ROI",
        )

    def land_opportunity_cost(
        self,
        quadrant: str,
        land_cost: float,
        expected_additional_profit: float,
        remaining_turns: int,
    ) -> OpportunityCost:
        if expected_additional_profit <= 0 or remaining_turns <= 0:
            return OpportunityCost(
                label=f"land_{quadrant}",
                cost=land_cost,
                description="Cost of land purchase with no expected return",
            )
        payback_turns = land_cost / expected_additional_profit
        cost = land_cost if payback_turns > remaining_turns else 0.0
        return OpportunityCost(
            label=f"land_{quadrant}",
            cost=cost,
            description=(
                f"Land {quadrant} payback takes {payback_turns:.1f} turns "
                f"(remaining: {remaining_turns})"
            ),
        )

    def calculate_all(
        self,
        state: Any,
        market_price_history: dict[str, list[float]],
    ) -> dict[str, float]:
        """Calculate all relevant opportunity costs for the current state."""
        costs: dict[str, float] = {}
        remaining_turns = getattr(state, "season", None)
        if remaining_turns is not None:
            remaining_turns = remaining_turns.remaining_turns
        else:
            remaining_turns = 720

        cash = getattr(state, "farm", None)
        cash = cash.money if cash else 3000.0

        costs["cash_reserve"] = self.cash_opportunity_cost(
            cash,
            alternative_roi=5.0,
            remaining_turns=remaining_turns,
        ).cost

        return costs
