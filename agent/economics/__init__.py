"""Stage 2 — Economic module exports."""

from __future__ import annotations

from agent.economics.capital_allocation import (
    CapitalAllocation,
    CapitalAllocator,
)
from agent.economics.economic_state import EconomicEvaluator, EconomicState
from agent.economics.opportunity_cost import (
    OpportunityCost,
    OpportunityCostEngine,
)
from agent.economics.profit_model import (
    ANIMAL_PARAMS,
    CROP_PARAMS,
    ProfitabilityEngine,
    ProfitabilityEstimate,
    estimate_animal_profitability,
    estimate_crop_profitability,
)

__all__ = [
    "ANIMAL_PARAMS",
    "CROP_PARAMS",
    "CapitalAllocation",
    "CapitalAllocator",
    "EconomicEvaluator",
    "EconomicState",
    "OpportunityCost",
    "OpportunityCostEngine",
    "ProfitabilityEngine",
    "ProfitabilityEstimate",
    "estimate_animal_profitability",
    "estimate_crop_profitability",
]
