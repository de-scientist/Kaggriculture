from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent.decision.candidate_actions import CandidateAction
from agent.economics.economic_state import EconomicEvaluator
from agent.economics.profit_model import ProfitabilityEstimate
from agent.market.market_intelligence import MarketIntelligenceEngine
from agent.optimization.crop_optimizer import CropOptimizer
from agent.optimization.animal_optimizer import AnimalOptimizer
from agent.optimization.worker_optimizer import WorkerOptimizer
from agent.optimization.land_optimizer import LandOptimizer
from agent.optimization.resource_optimizer import ResourceOptimizer
from agent.planning.planner import Planner
from agent.planning.rollout import RolloutEngine
from agent.simulation.simulator import SimulationEngine
from agent.strategies.adaptive_strategy import AdaptiveStrategyController
from agent.strategies.strategy_manager import StrategyManager
from agent.economics.economic_state import EconomicState
from agent.economics.opportunity_cost import OpportunityCostEngine
from agent.economics.capital_allocation import CapitalAllocator
from agent.market.price_tracker import PriceTracker
from agent.market.price_forecaster import PriceForecaster
from agent.market.demand_model import DemandModel


def decide(context: DecisionContext) -> dict[str, Any]:
    """Core decision engine.

    Orchestrates candidate generation, validation, strategy evaluation
    and action selection. Every decision turn is wrapped in the operational layer:

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

    start = time.perf_counter()
    config = context.config
    step = context.step or 0
    day = context.day or 0
    hour = context.hour or 0
    player = context.player
    strategy_name = config.get("strategy", {}).get("name", "baseline")
    seed = config.get("seed") if config else None

    tracer = get_default_tracer()
    trace = tracer.start_trace(step=step, day=day, player=player, strategy=strategy_name)

    perf = PerformanceBudget(config.get("performance", {}))
    metrics = get_metrics()
    telemetry = get_telemetry()
    replay = get_replay_store()

    game_state = context.game_state
    available_money = game_state.available_money() if game_state else 3000.0
    available_workers = len(game_state.available_workers()) if game_state else 1

    log = logger.bind(
        turn=step,
        day=day,
        player=player,
        strategy=strategy_name,
        correlation_id=trace.correlation_id,
        decision_id=trace.decision_id,
    )
    log.info(
        "Decision started",
        component="DecisionEngine",
        action="decide",
        worker_count=available_workers,
        available_money=available_money,
    )

    selected: CandidateAction = fallback.get_fallback()
    strategy_scores: dict[str, Any] = {}
    scored: list[Any] = []
    trace_record = decision_trace.DecisionTrace(step=step, day=day, strategy_name=strategy_name)
    action_dict: dict[str, Any] = {"farmer": ["PASS"], "hands": [], "market": []}
    failure: str | None = None

    try:
        with _timed_span(tracer, trace, "generate_candidates"):
            candidates = generate_candidates(context)
        trace_record.record_candidates(len(candidates))
        log.debug(
            "Generated %d candidates",
            len(candidates),
            component="DecisionEngine",
            action="generate_candidates",
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
                selected = scored[0].action
            else:
                selected = fallback.get_fallback()
            trace_record.record_final(selected)
            action_dict = _action_to_dict(selected)

    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        telemetry.record_exception(type(exc).__name__)
        trace_record.record_failure(failure)
        log.error(
            "Decision failed: %s",
            failure,
            exc_info=True,
            component="DecisionEngine",
            action="decide",
        )
        metrics.record_value("decision_failures", 1.0)
        if isinstance(exc, StrategyError) and "Performance budget" in str(exc):
            raise

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    telemetry.record_decision(elapsed_ms, strategy=strategy_name)
    _record_performance(perf, elapsed_ms, metrics)
    _log_decision_complete(log, trace, strategy_name, selected, scored, elapsed_ms)
    _record_replay(
        replay,
        step,
        day,
        hour,
        player,
        context.obs,
        trace,
        strategy_scores,
        action_dict,
        elapsed_ms,
    )
    trace_record.mark_complete(start)
    return action_dict