"""Core decision engine.

Orchestrates candidate generation, validation, strategy evaluation and action
selection.  Every decision turn is wrapped in the operational layer:

* a unique :class:`~agent.observability.tracing.Trace` (correlation +
  decision id) with timed spans per phase;
* structured logging of the decision;
* performance-budget checks against ``settings.performance``;
* cumulative :class:`~agent.observability.metrics.MetricsCollector`
  and :class:`~agent.observability.telemetry.Telemetry` updates;
* :class:`~agent.observability.replay.ReplayStore` recording for post-mortem
  analysis; and
* fail-fast exception handling with telemetry + safe fallback.
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Iterator

from agent.config.settings import Settings
from agent.decision import (
    action_filter,
    action_generator,
    action_validator,
    decision_context,
    decision_trace,
    fallback,
)
from agent.decision.candidate_actions import CandidateAction
from agent.exceptions.strategy import StrategyError
from agent.logging import get_logger
from agent.observability import (
    PerformanceBudget,
    ReplayStore,
    Trace,
    Tracer,
    get_metrics,
    get_replay_store,
    get_telemetry,
    get_default_tracer,
)
from agent.strategies import strategy_manager

logger = get_logger("agent.decision.engine")


def _normalise_config(config: Any) -> Settings:
    if isinstance(config, Settings):
        return config
    if isinstance(config, dict):
        known = {f.name for f in _settings_fields()}
        return Settings(**{k: v for k, v in config.items() if k in known})
    return Settings()


def _settings_fields() -> tuple:
    from dataclasses import fields

    return fields(Settings())


def _strategy_name(config: Any) -> str:
    return _normalise_config(config).strategy_name or "baseline"


def _seed(config: Any) -> int | None:
    if isinstance(config, Settings):
        return config.seed
    return (config or {}).get("seed") if isinstance(config, dict) else None


def _budget(config: Any) -> PerformanceBudget:
    return PerformanceBudget(_normalise_config(config).performance or {})


@contextmanager
def _timed_span(tracer: Tracer, trace: Trace, name: str) -> Iterator[None]:
    span = tracer.start_span(name, step=trace.step, day=trace.day)
    trace.add_span(span)
    try:
        yield
    finally:
        span.finish()


def _tracer_from_config(config: Any, seed: int | None, player: int) -> Tracer:
    tracer = get_default_tracer()
    if not tracer.correlation_id:
        from agent.observability.tracing import make_correlation_id

        tracer.set_correlation_id(make_correlation_id(seed, player))
    return tracer


def decide(context: decision_context.DecisionContext) -> dict:
    start = time.perf_counter()
    config = context.config
    step = context.step or _obs_field(context.obs, "step", 0)
    day = context.day or _obs_field(context.obs, "day", 0)
    hour = context.hour or _obs_field(context.obs, "hour", 0)
    player = context.player
    strategy_name = _strategy_name(config)
    seed = _seed(config)

    tracer = _tracer_from_config(config, seed, player)
    trace = tracer.start_trace(step=step, day=day, player=player, strategy=strategy_name)

    perf = _budget(config)
    metrics = get_metrics()
    telemetry = get_telemetry()
    replay = get_replay_store()

    game_state = context.game_state
    available_money = game_state.available_money() if game_state else 3000.0
    available_workers = len(game_state.available_workers()) if game_state else 1

    log = logger.bind(
        turn=step, day=day, player=player, strategy=strategy_name,
        correlation_id=trace.correlation_id, decision_id=trace.decision_id,
    )
    log.info(
        "Decision started",
        component="DecisionEngine", action="decide",
        worker_count=available_workers, available_money=available_money,
    )

    selected: CandidateAction = fallback.get_fallback()
    strategy_scores: dict[str, Any] = {}
    trace_record = decision_trace.DecisionTrace(step=step, day=day, strategy_name=strategy_name)
    action_dict: dict = {"farmer": ["PASS"], "hands": [], "market": []}
    failure: str | None = None

    try:
        with _timed_span(tracer, trace, "generate_candidates"):
            candidates = action_generator.generate_candidates(context)
        trace_record.record_candidates(len(candidates))
        log.debug(
            "Generated %d candidates", len(candidates),
            component="DecisionEngine", action="generate_candidates",
        )

        with _timed_span(tracer, trace, "filter_pre_validation"):
            filtered = action_filter.filter_pre_validation(
                candidates,
                available_money=available_money,
                available_workers=available_workers,
                owned_tiles=set(),
            )

        with _timed_span(tracer, trace, "validate"):
            validated = action_validator.validate_actions(filtered, game_state)
            trace_record.record_validation(validated)
            if any(not v.is_valid for v in validated):
                telemetry.record_failed_validation()

        valid = [v.action for v in validated if v.is_valid]

        with _timed_span(tracer, trace, "evaluate_strategy"):
            strategy = strategy_manager.get_strategy(strategy_name)
            scored = strategy.evaluate(context, valid)
            strategy_scores = _collect_scores(scored)
            trace_record.record_ranking(scored)

        with _timed_span(tracer, trace, "select_and_convert"):
            if scored:
                selected = scored[0]
            else:
                selected = fallback.get_fallback()
            trace_record.record_final(selected)
            action_dict = _action_to_dict(selected)

    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        telemetry.record_exception(type(exc).__name__)
        trace_record.record_failure(failure)
        log.error("Decision failed: %s", failure, exc_info=True,
                  component="DecisionEngine", action="decide")
        metrics.record_value("decision_failures", 1.0)
        if isinstance(exc, StrategyError) and "Performance budget" in str(exc):
            raise
        return {"farmer": ["PASS"], "hands": [], "market": []}

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    telemetry.record_decision(elapsed_ms, strategy=strategy_name)
    _record_performance(perf, elapsed_ms, metrics)
    _log_decision_complete(log, trace, strategy_name, selected, scored, elapsed_ms)
    _record_replay(
        replay, step, day, hour, player, context.obs, trace,
        strategy_scores, action_dict, elapsed_ms,
    )
    trace_record.mark_complete(start)
    return action_dict


# -- helpers --------------------------------------------------------------
def _obs_field(obs: dict, key: str, default: Any) -> Any:
    try:
        return obs.get(key, default)
    except Exception:
        return default


def _collect_scores(scored: list[Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    try:
        for s in scored:
            key = getattr(s.action, "id", getattr(s, "id", str(s)))
            result[key] = {
                "score": getattr(s, "score", None),
                "explanation": getattr(s, "explanation", ""),
            }
    except Exception:
        pass
    return result


def _record_performance(perf: PerformanceBudget, elapsed_ms: float, metrics) -> None:
    metrics.record_decision_time(elapsed_ms)
    result = perf.check("total_decision_ms", elapsed_ms)
    if result.status.value != "ok":
        logger.warning(
            "Performance budget %s for %s",
            result.status.value, result.component,
            component="PerformanceBudget", execution_time_ms=elapsed_ms,
        )
    metrics.record_value("decision_time_ms", elapsed_ms)


def _log_decision_complete(
    log, trace: Trace, strategy_name: str, selected: Any, scored: list, elapsed_ms: float
) -> None:
    if isinstance(selected, CandidateAction):
        action = selected.action_type
    else:
        action = "unknown"
    log.info(
        "Decision complete: selected %s from %d candidates", action, len(scored),
        component="DecisionEngine", action=action,
        strategy=strategy_name, execution_time_ms=round(elapsed_ms, 3),
    )


def _record_replay(
    replay: ReplayStore, step: int, day: int, hour: int, player: int,
    observation: dict | None, trace: Trace, strategy_scores: dict[str, Any],
    action_dict: dict, elapsed_ms: float,
) -> None:
    if not replay.enabled:
        return
    replay.record(
        turn=step, day=day, hour=hour, player=player,
        observation=observation or {}, trace=trace,
        strategy_scores=strategy_scores, selected_action=action_dict,
        execution_time_ms=elapsed_ms,
    )


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
