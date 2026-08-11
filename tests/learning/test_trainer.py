"""End-to-end training pipeline on synthetic experience."""

from __future__ import annotations

import json
from pathlib import Path

from agent.learning.model_registry import ModelRegistry
from agent.learning.models.bundle import LearnedBundle
from agent.learning.schema import FEATURE_VERSION
from agent.learning.trainer import fit_and_register


def _write_episode(
    root: Path,
    episode_id: str,
    n_rows: int,
    outcome: float,
    seed: int,
) -> None:
    rows = []
    for i in range(n_rows):
        rows.append(
            {
                "schema": 1,
                "episode_id": episode_id,
                "step": i,
                "day": i // 24,
                "hour": i % 24,
                "feature_version": FEATURE_VERSION,
                "farmer_action_type": "water" if i % 2 else "plant",
                "features": [
                    float(seed % 3),
                    float(i % 7) / 7.0,
                    float(seed) / 10.0,
                    1.0,
                    0.5,
                    0.0,
                ],
            }
        )
    (root / f"{episode_id}.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows), encoding="utf-8"
    )


def _write_manifest(root: Path, episodes: list[tuple[str, float]]) -> None:
    lines = [
        json.dumps({"episode_id": eid, "outcome_money": outcome, "opponent": "random", "seed": 1})
        for eid, outcome in episodes
    ]
    (root / "manifest.jsonl").write_text("\n".join(lines), encoding="utf-8")


def test_fit_and_register_end_to_end(tmp_path: Path) -> None:
    exp = tmp_path / "experiences"
    exp.mkdir()
    episodes = [(f"ep{i}", 4000.0 + i * 500.0) for i in range(8)]
    for i, (eid, outcome) in enumerate(episodes):
        _write_episode(exp, eid, n_rows=48, outcome=outcome, seed=i)
    _write_manifest(exp, episodes)

    model_dir = tmp_path / "models"
    result = fit_and_register(
        experiences_dir=exp,
        model_dir=model_dir,
        dataset_version="d1",
        seed=0,
        note="synthetic",
    )
    metrics = result["metrics"]
    model_id = result["model_id"]
    assert "value_train_rmse" in metrics
    assert "policy_train_acc" in metrics
    assert "value_test_rmse" in metrics
    assert metrics["n_episodes_train"] > 0
    assert metrics["n_episodes_test"] > 0

    bundle_path = Path(result["bundle_dir"]) / "model.json"
    bundle = LearnedBundle.load(str(bundle_path))
    assert bundle.is_ready()
    assert bundle.feature_version == FEATURE_VERSION

    reg = ModelRegistry(model_dir)
    entry = reg.get(model_id)
    assert entry.status == "experimental"
    assert entry.feature_version == FEATURE_VERSION


def test_fit_and_register_raises_without_episodes(tmp_path: Path) -> None:
    import pytest

    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ValueError):
        fit_and_register(experiences_dir=empty, model_dir=tmp_path / "m")
