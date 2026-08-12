"""Integration tests for the decision engine with full observability wiring."""

from __future__ import annotations

from typing import Any

import pytest

from agent.adapters import ObservationAdapter
from agent.config import load_config
from agent.decision import action_generator, decision_context, decision_engine
from agent.observability import get_metrics, get_replay_store, get_telemetry

SAMPLE_OBS = {
    "player": 0,
    "step": 1,
    "day": 0,
    "hour": 0,
    "remaining_turns": 720,
    "farms": [
        {
            "money": 3000,
            "tiles": [[None]],
            "farmer": [0, 0],
            "hands": [],
            "unlocked_quadrants": ["NW"],
            "hires_today": 0,
        },
        {
            "money": 3000,
            "tiles": [[None]],
            "farmer": [0, 0],
            "hands": [],
            "unlocked_quadrants": ["NW"],
            "hires_today": 0,
        },
    ],
    "private": {"shed": {}, "seeds": {}, "inventories": [{}]},
    "market": {"inventory": {}, "prices": {}},
    "town": {"unlocked_shops": []},
}


def _context(
    config: Any | None = None, game_state: Any | None = None
) -> decision_context.DecisionContext:
    settings = config or load_config("development")
    if game_state is None:
        game_state = ObservationAdapter().parse(SAMPLE_OBS)
    return decision_context.DecisionContext(
        obs=SAMPLE_OBS,
        player=0,
        game_state=game_state,
        config=settings,
        step=1,
        day=0,
        hour=0,
        remaining_turns=720,
        strategy_name=settings.strategy_name,
    )


def test_decide_returns_valid_kaggle_action() -> None:
    ctx = _context()
    action = decision_engine.decide(ctx)
    assert set(action.keys()) == {"farmer", "hands", "market"}
    assert isinstance(action["farmer"], list)
    assert isinstance(action["hands"], list)
    assert isinstance(action["market"], list)


def test_decide_records_telemetry_metrics_replay() -> None:
    telem = get_telemetry()
    metrics = get_metrics()
    replay = get_replay_store()
    assert telem.decisions == 0
    decision_engine.decide(_context())
    assert telem.decisions == 1
    assert metrics.counter("decision_count") == 1.0
    assert len(replay.records()) == 1


def test_decide_records_trace_spans() -> None:
    decision_engine.decide(_context())
    rec = get_replay_store().records()[0]
    span_names = [s.get("name") for s in rec.trace.get("spans", [])]
    for expected in (
        "generate_candidates",
        "filter_pre_validation",
        "validate",
        "evaluate_strategy",
        "select_and_convert",
    ):
        assert expected in span_names


def test_decide_records_strategy_scores() -> None:
    decision_engine.decide(_context())
    rec = get_replay_store().records()[0]
    assert rec.strategy_scores
    assert rec.decision_id == "d-1"


def test_decide_records_execution_time_in_replay() -> None:
    decision_engine.decide(_context())
    rec = get_replay_store().records()[0]
    assert rec.execution_time_ms >= 0.0


def test_decide_fallback_returns_pass_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """When a pipeline phase raises, decide returns PASS and records the error."""
    import agent.decision.decision_engine as de

    def boom(_ctx: Any) -> Any:
        raise ValueError("candidate generation exploded")

    monkeypatch.setattr(action_generator, "generate_candidates", boom)
    action = decision_engine.decide(_context())
    assert action == {"farmer": ["PASS"], "hands": [], "market": []}
    assert "ValueError" in get_telemetry().snapshot().exception_counts
    assert get_metrics().counter("decision_count") == 1.0


def test_decision_performance_budget_strategy_error_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A StrategyError mentioning 'Performance budget' is not swallowed by decide."""
    from agent.exceptions.strategy import StrategyError

    class _Budget:
        def check(self, *a: Any, **k: Any) -> Any:
            raise StrategyError("Performance budget exceeded for DecisionEngine")

    monkeypatch.setattr(decision_engine, "_budget", lambda config: _Budget())
    with pytest.raises(StrategyError, match="Performance budget"):
        decision_engine.decide(_context())
