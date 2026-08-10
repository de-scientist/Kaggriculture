"""Kaggriculture AI agent entry point.

This module provides the ``agent(obs)`` function invoked by the Kaggle
environment each turn.  It is the composition root for the operational layer:

* loads and validates centralized :class:`~agent.config.settings.Settings`;
* configures structured logging (:func:`~agent.logging.configure_logging`);
* initialises a deterministic tracing :class:`~agent.observability.tracing.Tracer`;
* adapts the raw observation, runs the :class:`~agent.decision.decision_engine`
  (which itself emits traces, metrics, telemetry and replay records), and
* serialises the resulting action to the official Kaggle format.

Any unexpected error is logged, recorded in telemetry, and recovered from
with a safe ``PASS`` fallback so a single turn never kills the episode.
"""

from __future__ import annotations

import time
from typing import Any

from agent.adapters import ActionAdapter, ObservationAdapter
from agent.config import Settings, get_config
from agent.decision import DecisionContext, decision_engine
from agent.exceptions.adapter import ObservationParseError
from agent.logging import configure_logging, get_logger
from agent.observability import get_default_tracer, get_telemetry
from agent.observability.tracing import make_correlation_id

logger = get_logger("agent.agent")

_adapter: ObservationAdapter | None = None
_action_adapter: ActionAdapter | None = None
_initialized: bool = False
_tracer_initialized: bool = False


def _ensure_initialized() -> Settings:
    global _adapter, _action_adapter, _initialized
    settings = get_config()
    if not _initialized:
        configure_logging(settings, force=True)
        _adapter = ObservationAdapter()
        _action_adapter = ActionAdapter()
        _initialized = True
    return settings


def _set_player_correlation(player: int, seed: int | None) -> None:
    global _tracer_initialized
    tracer = get_default_tracer()
    if not tracer.correlation_id:
        tracer.set_correlation_id(make_correlation_id(seed, player))
    _tracer_initialized = True


def agent(obs: dict[str, Any]) -> dict[str, Any]:
    """Return a Kaggle-formatted action dict for the current observation.

    Args:
        obs: Raw observation from the Kaggle environment.

    Returns:
        ``{"farmer": [...], "hands": [...], "market": [...]}``
    """
    settings = _ensure_initialized()
    start = time.perf_counter()
    try:
        player = int(obs.get("player", 0))
        _set_player_correlation(player, settings.seed)

        assert _adapter is not None and _action_adapter is not None
        game_state = _adapter.parse(obs)
        step = int(obs.get("step", 0))
        day = int(obs.get("day", 0))
        hour = int(obs.get("hour", 0))

        context = DecisionContext(
            obs=obs,
            player=player,
            game_state=game_state,
            config=settings,
            step=step,
            day=day,
            hour=hour,
            remaining_turns=int(obs.get("remaining_turns", 720)),
            strategy_name=settings.strategy_name,
        )

        action = decision_engine.decide(context)
        kaggle_action = _action_adapter.convert(action)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        logger.performance("Agent", elapsed_ms, turn=step, day=day, player=player)
        return kaggle_action

    except ObservationParseError as exc:
        telemetry = get_telemetry()
        telemetry.record_exception("ObservationParseError")
        logger.error(
            "Observation parse error: %s",
            exc,
            exc_info=True,
            component="ObservationAdapter",
            action="parse",
        )
        return {"farmer": ["PASS"], "hands": [], "market": []}
    except Exception as exc:
        telemetry = get_telemetry()
        telemetry.record_exception(type(exc).__name__)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        logger.error(
            "Agent error: %s",
            exc,
            exc_info=True,
            component="Agent",
            action="agent",
            execution_time_ms=round(elapsed_ms, 3),
        )
        return {"farmer": ["PASS"], "hands": [], "market": []}
