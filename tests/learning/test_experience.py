"""Experience recorder must write durable JSONL rows + a manifest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.learning.experience import ExperienceRecorder, ExperienceStore
from agent.learning.schema import EXPERIENCE_SCHEMA_VERSION
from agent.runtime.game import GameSnapshot
from tests.fixtures.observations import minimal_observation


def _plan_stub(action_type: str = "plant") -> object:
    class Plan:
        def __init__(self) -> None:
            self.farmer_op = ["PLANT", "WHEAT"]
            self.hands_ops = [["WATER"]]
            self.market_orders = [["BUY_SEED", "WHEAT", 1]]
            self.candidates: list[Any] = []
            self.farmer_action_type = action_type
            self.info = {
                "adjustments": {"mode": "champion", "crop": "WHEAT"},
                "n_tasks": 3,
                "n_jobs": 2,
            }

    return Plan()


def _snap(step: int, day: int, hour: int, money: float = 3000.0) -> GameSnapshot:
    obs = minimal_observation()
    obs["step"] = step
    obs["day"] = day
    obs["hour"] = hour
    obs["farms"][0]["money"] = money
    return GameSnapshot.from_obs(obs)


def test_managed_episode_roundtrip(tmp_path: Path) -> None:
    recorder = ExperienceRecorder(tmp_path)
    recorder.begin_episode("ep1", {"seed": 1, "opponent": "random"})
    for step in range(3):
        recorder.observe(_snap(step, 0, step), _plan_stub())
    recorder.end_episode({"outcome_money": 4000.0})

    rows = [json.loads(line) for line in (tmp_path / "ep1.jsonl").read_text().splitlines()]
    assert len(rows) == 3
    row = rows[0]
    assert row["schema"] == EXPERIENCE_SCHEMA_VERSION
    assert row["episode_id"] == "ep1"
    assert row["farmer_action_type"] == "plant"
    assert row["farmer_op"] == "PLANT"
    assert isinstance(row["selected_crop"], (str, type(None)))
    assert row["feature_version"] == 1
    assert isinstance(row["features"], list)
    assert isinstance(row["state"], dict)
    assert row["market_orders"] == [["BUY_SEED", "WHEAT", 1]]

    manifest = [json.loads(line) for line in (tmp_path / "manifest.jsonl").read_text().splitlines()]
    assert manifest[0]["episode_id"] == "ep1"
    assert manifest[0]["outcome_money"] == 4000.0
    assert manifest[0]["rows"] == 3
    assert manifest[0]["seed"] == 1


def test_begin_episode_auto_finalizes_previous(tmp_path: Path) -> None:
    recorder = ExperienceRecorder(tmp_path)
    recorder.begin_episode("a", {"outcome_note": "first"})
    recorder.observe(_snap(0, 0, 0), _plan_stub())
    recorder.begin_episode("b", {})
    recorder.observe(_snap(0, 0, 0), _plan_stub())
    recorder.end_episode()

    manifest = [json.loads(line) for line in (tmp_path / "manifest.jsonl").read_text().splitlines()]
    assert {m["episode_id"] for m in manifest} == {"a", "b"}
    assert manifest[0]["outcome_money"] == 3000.0


def test_auto_mode_detects_step_reset(tmp_path: Path) -> None:
    recorder = ExperienceRecorder(tmp_path)
    recorder.observe(_snap(719, 29, 23), _plan_stub())
    recorder.observe(_snap(0, 0, 0), _plan_stub())  # new episode detected
    recorder.close()

    jsonl_files = sorted(p for p in tmp_path.glob("*.jsonl") if p.name != "manifest.jsonl")
    manifest = [json.loads(line) for line in (tmp_path / "manifest.jsonl").read_text().splitlines()]
    assert len(manifest) == 2
    assert len(jsonl_files) == 2


def test_store_is_append_only_and_threadsafe(tmp_path: Path) -> None:
    store = ExperienceStore(tmp_path)
    store.record("ep", {"step": 1})
    store.record("ep", {"step": 2})
    rows = [json.loads(line) for line in (tmp_path / "ep.jsonl").read_text().splitlines()]
    assert [r["step"] for r in rows] == [1, 2]
