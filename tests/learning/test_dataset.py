"""Dataset construction, splits, and leakage validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.learning.dataset import (
    ExperienceEpisode,
    build_dataset,
    dataset_summary,
    load_episodes,
    split_episodes,
    validate_no_leakage,
)
from agent.learning.schema import FEATURE_VERSION


def _episode(episode_id: str, n_rows: int, outcome: float, seed: int = 1) -> ExperienceEpisode:
    rows = [
        {
            "schema": 1,
            "episode_id": episode_id,
            "step": i,
            "day": i // 24,
            "feature_version": FEATURE_VERSION,
            "farmer_action_type": "plant" if i % 2 else "water",
            "state": {"money": 3000.0 + i},
            "features": [0.5] * 3,
        }
        for i in range(n_rows)
    ]
    return ExperienceEpisode(
        episode_id=episode_id,
        rows=rows,
        meta={"seed": seed, "opponent": "random", "outcome_money": outcome},
    )


def _write_experiences(root: Path) -> None:
    for eid, n, outcome in [("e1", 3, 5000.0), ("e2", 4, 7000.0), ("e3", 2, 4000.0)]:
        (root / f"{eid}.jsonl").write_text(
            "\n".join(json.dumps(r) for r in _episode(eid, n, outcome).rows), encoding="utf-8"
        )
    (root / "manifest.jsonl").write_text(
        "\n".join(
            json.dumps({"episode_id": eid, "outcome_money": outcome, "opponent": "random"})
            for eid, _, outcome in [("e1", 0, 5000.0), ("e2", 0, 7000.0), ("e3", 0, 4000.0)]
        ),
        encoding="utf-8",
    )


def test_load_episodes_from_logs(tmp_path: Path) -> None:
    _write_experiences(tmp_path)
    episodes = load_episodes(tmp_path)
    assert {e.episode_id for e in episodes} == {"e1", "e2", "e3"}
    assert {e.outcome for e in episodes} == {5000.0, 7000.0, 4000.0}


def test_episode_outcome_falls_back_to_last_row(tmp_path: Path) -> None:
    (tmp_path / "x.jsonl").write_text(
        "\n".join(json.dumps(r) for r in _episode("x", 3, 9999.0).rows), encoding="utf-8"
    )
    episodes = load_episodes(tmp_path)
    assert episodes[0].outcome == 3000.0 + 2  # last row money


def test_split_is_episode_level_and_no_leakage() -> None:
    episodes = [_episode(f"e{i}", 10, 5000.0, seed=i) for i in range(10)]
    splits = split_episodes(episodes, seed=0)
    all_ids = [e.episode_id for group in splits.values() for e in group]
    assert len(all_ids) == len(set(all_ids)) == 10
    assert validate_no_leakage(splits) == []
    assert set(splits) == {"train", "val", "test"}


def test_split_deterministic_under_seed() -> None:
    episodes = [_episode(f"e{i}", 10, 5000.0, seed=i) for i in range(10)]
    a = split_episodes(episodes, seed=5)
    b = split_episodes(episodes, seed=5)
    assert [e.episode_id for e in a["train"]] == [e.episode_id for e in b["train"]]


def test_split_ratios_must_sum_to_one() -> None:
    with pytest.raises(ValueError):
        split_episodes([_episode("e", 1, 1.0)], train_ratio=0.5, val_ratio=0.2, test_ratio=0.1)


def test_build_dataset_labels() -> None:
    episodes = [_episode("e1", 4, 6000.0)]
    ds = build_dataset(episodes)
    assert len(ds) == 4
    assert all(v == 6000.0 for v in ds.value_labels)
    assert set(ds.policy_labels) <= {"plant", "water"}
    assert len(set(ds.episode_ids)) == 1


def test_build_dataset_rejects_wrong_feature_version() -> None:
    episode = _episode("e1", 2, 5000.0)
    episode.rows[0]["feature_version"] = 999
    with pytest.raises(ValueError):
        build_dataset([episode])


def test_dataset_summary_shape() -> None:
    ds = build_dataset([_episode("e1", 4, 6000.0)])
    summary = dataset_summary(ds)
    assert summary["rows"] == 4
    assert summary["episodes"] == 1
    assert summary["n_action_types"] == 2
