from __future__ import annotations

from agent.decision.candidate_actions import CandidateAction

WEIGHTS = {
    "profit": 1.0,
    "worker_efficiency": 0.3,
    "time_efficiency": 0.2,
    "inventory_impact": 0.15,
    "market_opportunity": 0.25,
    "resource_sustainability": 0.1,
    "action_cost": -0.5,
    "opportunity_cost": -0.2,
}


def compute_profit_score(action: CandidateAction) -> float:
    return max(0.0, action.estimated_reward)


def compute_worker_efficiency_score(action: CandidateAction) -> float:
    if action.worker:
        return 1.0
    return 0.5


def compute_time_efficiency_score(action: CandidateAction) -> float:
    atype = action.action_type.lower()
    if atype in ("harvest", "sell", "feed"):
        return 1.0
    if atype in ("plant", "water"):
        return 0.7
    return 0.3


def compute_inventory_impact_score(action: CandidateAction) -> float:
    if action.estimated_reward > 0:
        return 0.5
    return 0.0


def compute_market_opportunity_score(action: CandidateAction) -> float:
    atype = action.action_type.lower()
    if atype in ("sell", "buy_product"):
        return 1.0
    return 0.2


def compute_resource_sustainability_score(action: CandidateAction) -> float:
    if action.estimated_cost <= 0:
        return 1.0
    return 0.5


def compute_action_cost_penalty(action: CandidateAction) -> float:
    return -action.estimated_cost * WEIGHTS["action_cost"]


def compute_opportunity_cost_penalty(action: CandidateAction) -> float:
    return -abs(action.estimated_reward - action.estimated_cost) * WEIGHTS["opportunity_cost"]


def score_action(action: CandidateAction) -> tuple[float, str]:
    profit = compute_profit_score(action)
    worker = compute_worker_efficiency_score(action)
    time_eff = compute_time_efficiency_score(action)
    inventory = compute_inventory_impact_score(action)
    market = compute_market_opportunity_score(action)
    sustainability = compute_resource_sustainability_score(action)
    cost_penalty = compute_action_cost_penalty(action)
    opp_cost_penalty = compute_opportunity_cost_penalty(action)

    total = (
        profit * WEIGHTS["profit"]
        + worker * WEIGHTS["worker_efficiency"]
        + time_eff * WEIGHTS["time_efficiency"]
        + inventory * WEIGHTS["inventory_impact"]
        + market * WEIGHTS["market_opportunity"]
        + sustainability * WEIGHTS["resource_sustainability"]
        + cost_penalty
        + opp_cost_penalty
    )

    explanation = (
        f"profit={profit:.1f}, worker={worker:.1f}, "
        f"time={time_eff:.1f}, inv={inventory:.1f}, "
        f"market={market:.1f}, sustain={sustainability:.1f}, "
        f"cost_penalty={cost_penalty:.1f}"
    )

    return total, explanation
