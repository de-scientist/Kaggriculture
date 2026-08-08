"""Tests for the replay store."""
from __future__ import annotations

import json
from pathlib import Path

from agent.observability import reset_replay_store
from agent.observability.replay import (
    ReplayStore,
    observation_hash,
)
from agent.observability.tracing import Trace


def test_observation_hash_is_deterministic() -> None:
    obs = {"player": 0, "step": 1}
    assert observation_hash(obs) == observation_hash({"player": 0, "step": 1})
    assert observation_hash(obs) != observation_hash({"player": 1, "step": 1})


def test_record_disabled_store_returns_none() -> None:
    store = ReplayStore(enabled=False)
    rec = store.record(turn=1, day=0, hour=0, player=0,
                       observation={}, selected_action={"farmer": ["PASS"]}, execution_time_ms=1.0)
    assert rec is None
    assert store.records() == []


def test_record_creates_replay_record() -> None:
    store = reset_replay_store()
    trace = Trace(correlation_id="c-1", decision_id="d-5", step=5, day=1,
                  player=0, strategy="baseline")
    rec = store.record(
        turn=5, day=1, hour=3, player=0,
        observation={"player": 0, "step": 5},
        trace=trace,
        strategy_scores={"pass_0": {"score": 0.3}},
        selected_action={"farmer": ["PASS"], "hands": [], "market": []},
        execution_time_ms=12.345,
    )
    assert rec is not None
    assert rec.turn == 5
    assert rec.decision_id == "d-5"
    assert rec.correlation_id == "c-1"
    assert rec.observation_hash == observation_hash({"player": 0, "step": 5})
    assert rec.strategy_scores["pass_0"]["score"] == 0.3
    assert rec.selected_action["farmer"] == ["PASS"]
    assert rec.trace["correlation_id"] == "c-1"


def test_find_by_turn() -> None:
    store = reset_replay_store()
    store.record(turn=1, day=0, hour=0, player=0, observation={},
                 selected_action={"farmer": ["PASS"]}, execution_time_ms=1.0)
    store.record(turn=2, day=0, hour=1, player=0, observation={},
                 selected_action={"farmer": ["PASS"]}, execution_time_ms=1.0)
    assert len(store.find(turn=1)) == 1
    assert len(store.find(turn=2)) == 1
    assert len(store.find()) == 2


def test_find_by_decision_id() -> None:
    from agent.observability.tracing import Trace

    store = reset_replay_store()
    trace = Trace(correlation_id="c-1", decision_id="d-1", step=1, day=0,
                  player=0, strategy="baseline")
    store.record(turn=1, day=0, hour=0, player=0, observation={}, trace=trace,
                 selected_action={"farmer": ["PASS"]}, execution_time_ms=1.0)
    assert len(store.find(decision_id="d-1")) == 1
    assert store.find(decision_id="d-1")[0].decision_id == "d-1"
    assert len(store.find(decision_id="d-99")) == 0


def test_to_dict_and_clear() -> None:
    store = reset_replay_store()
    store.record(turn=1, day=0, hour=0, player=0, observation={},
                 selected_action={"farmer": ["PASS"]}, execution_time_ms=1.0)
    d = store.to_dict()
    assert d["count"] == 1
    assert d["records"][0]["turn"] == 1
    store.clear()
    assert store.records() == []
    assert store.to_dict()["count"] == 0


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    store = ReplayStore(enabled=True, directory=str(tmp_path))
    store.record(turn=7, day=2, hour=4, player=0, observation={"player": 0},
                 selected_action={"farmer": ["PASS"], "hands": [], "market": []},
                 execution_time_ms=9.0)
    out = store.save(path=tmp_path / "replay.json")
    loaded = ReplayStore.load(out)
    assert loaded.enabled is True
    assert len(loaded.records()) == 1
    assert loaded.records()[0].turn == 7
    # raw file is valid JSON
    with open(out, encoding="utf-8") as f:
        json.load(f)
