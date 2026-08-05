from __future__ import annotations

import time

from agent.decision import (
    action_filter,
    action_generator,
    action_validator,
    decision_context,
    decision_trace,
    fallback,
)
from agent.decision.candidate_actions import CandidateAction
from agent.strategies import strategy_manager


def decide(context: decision_context.DecisionContext) -> dict:
    start = time.perf_counter()
    trace = decision_trace.DecisionTrace(
        step=context.step,
        day=context.day,
        strategy_name=context.config.get("strategy", {}).get("name", "baseline"),
    )

    candidates = action_generator.generate_candidates(context)
    trace.record_candidates(len(candidates))

    filtered = action_filter.filter_pre_validation(
        candidates,
        available_money=context.game_state.available_money() if context.game_state else 3000.0,
        available_workers=len(context.game_state.available_workers()) if context.game_state else 1,
        owned_tiles=set(),
    )

    validated = action_validator.validate_actions(filtered, context.game_state)
    trace.record_validation(validated)

    valid = [v.action for v in validated if v.is_valid]

    strategy_name = context.config.get("strategy", {}).get("name", "baseline") if context.config else "baseline"
    strategy = strategy_manager.get_strategy(strategy_name)
    scored = strategy.evaluate(context, valid)
    trace.record_ranking(scored)

    if not scored:
        best = fallback.get_fallback()
        trace.record_final(best)
        trace.mark_complete(start)
        return _action_to_dict(best)

    best = scored[0]
    trace.record_final(best)
    trace.mark_complete(start)
    return _action_to_dict(best)


def _action_to_dict(action: object) -> dict:
    if isinstance(action, dict):
        return action
    if isinstance(action, CandidateAction):
        atype = action.action_type.lower()
        if atype in ("pass",):
            return {"farmer": ["PASS"], "hands": [], "market": []}
        if atype in ("harvest",):
            return {"farmer": ["HARVEST"], "hands": [], "market": []}
        if atype in ("water",):
            return {"farmer": ["WATER"], "hands": [], "market": []}
        if atype in ("plant",):
            return {"farmer": ["PLANT", "WHEAT"], "hands": [], "market": []}
        if atype in ("sell",):
            return {"farmer": ["PASS"], "hands": [], "market": [["SELL", "WHEAT", 1]]}
        if atype in ("buy_seed", "buy_product", "buy_animal"):
            return {"farmer": ["PASS"], "hands": [], "market": [["BUY_SEED", "WHEAT", 1]]}
        if atype in ("hire",):
            return {"farmer": ["PASS"], "hands": [], "market": [["HIRE"]]}
        if atype in ("feed",):
            return {"farmer": ["FEED"], "hands": [], "market": []}
        if atype in ("care",):
            return {"farmer": ["CARE"], "hands": [], "market": []}
        if atype in ("collect_fertilizer",):
            return {"farmer": ["COLLECT_FERTILIZER"], "hands": [], "market": []}
        return {"farmer": ["PASS"], "hands": [], "market": []}
    return {"farmer": ["PASS"], "hands": [], "market": []}
