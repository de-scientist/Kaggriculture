from __future__ import annotations

import time

from agent.decision import action_filter
from agent.decision import action_generator
from agent.decision import action_ranker
from agent.decision import action_validator
from agent.decision import decision_context
from agent.decision import decision_trace
from agent.decision import fallback
from agent.decision import utility_score
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

    strategy = strategy_manager.get_strategy(context.config)
    scored = strategy.rank(valid, context)
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
        return {"action_type": action.action_type, "id": action.id}
    return {"farmer": ["PASS"], "hands": [], "market": []}