from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RiskAssessment:
    risk_level: str
    risk_score: float
    downside: float
    uncertainty: float
    mitigation: str
    recommended: str


class RiskEvaluator:
    """Evaluates risk of each action.

    Models:
    * Expected Value
    * Downside Risk
    * Uncertainty
    * Risk Penalty
    """

    def __init__(self):
        self._risk_weights = {
            "high": 0.3,
            "medium": 0.15,
            "low": 0.05,
        }

    def assess(
        self,
        action: Any,
        economic_state: Any,
        context: Any,
    ) -> RiskAssessment:
        risk = 0.0
        score = 0.0

        if action.estimated_cost > economic_state.available_capital:
            risk += 1.0
            score -= 50.0
        elif economic_state.remaining_turns < 50 and action.estimated_cost > 0:
            risk += 0.5
            score -= 10.0

        if action.estimated_reward > 0 and action.estimated_cost > 0:
            profit_ratio = action.estimated_reward / max(action.estimated_cost, 0.01)
            if profit_ratio < 1.0:
                risk += 0.3
                score -= 20.0

        return RiskAssessment(
            risk_level="low" if risk < 0.3 else "high" if risk > 0.7 else "medium",
            risk_score=risk,
            downside=0.0,
            uncertainty=0.0,
            mitigation="",
            recommended="",
        )

    def compute_risk_penalty(
        self,
        expected_value: float,
        downside: float,
        uncertainty: float,
    ) -> float:
        return expected_value * (1.0 - downside) / (1.0 + uncertainty)
