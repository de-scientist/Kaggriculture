from __future__ import annotations

from agent.decision.candidate_actions import CandidateAction


def score_harvest(action: CandidateAction) -> float:
    return action.estimated_reward * 1.5


def score_plant(action: CandidateAction) -> float:
    return action.estimated_reward * 0.8


def score_water(action: CandidateAction) -> float:
    return action.estimated_reward * 0.5


def score_feed(action: CandidateAction) -> float:
    return action.estimated_reward * 1.2


def score_sell(action: CandidateAction) -> float:
    return action.estimated_reward * 1.3


def score_buy(action: CandidateAction) -> float:
    return action.estimated_reward * 0.6


def score_hire(action: CandidateAction) -> float:
    return action.estimated_reward * 0.4


def score_idle(action: CandidateAction) -> float:
    return 0.0


def compute_utility(action: CandidateAction) -> float:
    action_type = action.action_type.lower()
    if action_type == "harvest":
        return score_harvest(action)
    if action_type == "plant":
        return score_plant(action)
    if action_type == "water":
        return score_water(action)
    if action_type == "feed":
        return score_feed(action)
    if action_type == "sell":
        return score_sell(action)
    if action_type in ("buy_seed", "buy_product", "buy_animal"):
        return score_buy(action)
    if action_type == "hire":
        return score_hire(action)
    if action_type == "pass":
        return score_idle(action)
    return action.net_value
