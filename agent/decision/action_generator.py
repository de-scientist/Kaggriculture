from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext


def generate_candidates(context: DecisionContext) -> list[CandidateAction]:
    """Generate candidate actions using economic reasoning."""
    candidates: list[CandidateAction] = []

    game_state = context.game_state
    if not game_state:
        return candidates

    farm = game_state.farm if hasattr(game_state, "farm") else None
    private = game_state.private if hasattr(game_state, "private") else {}
    seeds = private.get("seeds", {}) if hasattr(game_state, "private") else {}
    shed = private.get("shed", {}) if hasattr(game_state, "private") else {}
    market = game_state.market if hasattr(game_state, "market") else None
    if not market:
        market = {}

    # Market actions
    if market and hasattr(market, "prices"):
        prices = market.prices
    else:
        prices = {}

    # Seed purchase
    if seeds and context.remaining_turns > 0:
        for crop, count in seeds.items():
            if count > 0 and crop in prices:
                candidates.append(
                    CandidateAction(
                        id=f"buy_seed_{crop}",
                        action_type="buy_seed",
                        target_entity=crop,
                        estimated_cost=prices[crop],
                        estimated_reward=15.0,
                        metadata={"priority": 1},
                        strategy_annotations={"crop": crop},
                    )
                )

    # Sell from shed
    wheat_in_shed = shed.get("WHEAT", 0)
    if wheat_in_shed > 0:
        candidates.append(
            CandidateAction(
                id="sell_wheat",
                action_type="sell",
                estimated_reward=8.0,
                metadata={"priority": 2},
            )
        )

    # Harvest
    for pos, tile in (farm or {}).items() if (farm or {}) else []:
        if isinstance(tile, dict) and tile.get("kind") == "PLANT":
            crop_age = context.day - tile.get("planted_day", context.day)
            if crop_age >= 2:
                candidates.append(
                    CandidateAction(
                        id=f"harvest_{pos}",
                        action_type="harvest",
                        estimated_reward=10.0,
                        metadata={"priority": 3},
                    )
                )

    # Water
    for pos, tile in (farm or {}).items() if (farm or {}) else []:
        if isinstance(tile, dict) and tile.get("kind") == "PLANT":
            if not tile.get("watered_today", False):
                candidates.append(
                    CandidateAction(
                        id=f"water_{pos}",
                        action_type="water",
                        estimated_cost=0.0,
                        estimated_reward=5.0,
                        metadata={"priority": 4},
                    )
                )

    # Fertilize
    for pos, tile in (farm or {}).items() if (farm or {}) else []:
        if isinstance(tile, dict) and tile.get("kind") == "PLANT":
            if tile.get("consecutive_unwatered", 0) > 0 and tile.get("yield_units", 0) > 0:
                candidates.append(
                    CandidateAction(
                        id=f"fertilize_{pos}",
                        action_type="fertilize",
                        estimated_cost=0.0,
                        estimated_reward=5.0,
                        metadata={"priority": 5},
                    )
                )

    # Plant
    if seeds and context.remaining_turns > 0:
        candidates.append(
            CandidateAction(
                id="plant_0",
                action_type="plant",
                estimated_cost=10.0,
                estimated_reward=15.0,
                metadata={"priority": 6},
            )
        )

    # Market buy actions
    if market and hasattr(market, "inventory"):
        inventory = market.inventory
        for product in inventory:
            if inventory.get(product, 0) < 5:
                candidates.append(
                    CandidateAction(
                        id=f"buy_product_{product}",
                        action_type="buy_product",
                        estimated_cost=2.0,
                        estimated_reward=8.0,
                        metadata={"priority": 7},
                    )
                )

    # Animal actions
    if market and hasattr(market, "inventory"):
        inventory = market.inventory
        for product in inventory:
            if inventory.get(product, 0) < 3:
                candidates.append(
                    CandidateAction(
                        id=f"buy_animal_{product}",
                        action_type="buy_animal",
                        estimated_cost=5.0,
                        estimated_reward=12.0,
                        metadata={"priority": 8},
                    )
                )

    # Hire
    candidates.append(
        CandidateAction(
            id="hire",
            action_type="hire",
            estimated_cost=0.0,
            estimated_reward=3.0,
            metadata={"priority": 9},
        )
    )

    # Pass
    candidates.append(
        CandidateAction(
            id="pass",
            action_type="pass",
            estimated_cost=0.0,
            estimated_reward=0.0,
            metadata={"priority": 99},
        )
    )

    return candidates