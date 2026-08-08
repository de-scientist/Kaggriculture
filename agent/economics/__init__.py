"""Stage 2 — Economic module exports."""
from __future__ import annotations

from agent.economics.economic_state import EconomicEvaluator, EconomicState
from agent.economics.opportunity_cost import (
    OpportunityCost,
    OpportunityCostEngine,
)
from agent.economics.capital_allocation import (
    CapitalAllocation,
    CapitalAllocator,
)
from agent.economics.profit_model import (
    CROP_PARAMS,
    ANIMAL_PARAMS,
    ProfitabilityEstimate,
    estimate_animal_profitability,
    estimate_crop_profitability,
)

__all__ = [
    "EconomicEvaluator",
    "EconomicState",
    "OpportunityCost",
    "OpportunityCostEngine",
    "CapitalAllocation",
    "CapitalAllocator",
    "ProfitabilityEstimate",
    "CROP_PARAMS",
    "ANIMAL_PARAMS",
    "estimate_crop_profitability",
    "estimate_animal_profitability",
]
