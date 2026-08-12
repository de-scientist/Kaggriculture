"""Replay buffer: bounded storage, seeded sampling, JSON roundtrip."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.learning.replay_buffer import PrioritizedReplayBuffer


def _rows(n: int) -> list[dict[str, Any]]:
    return [{"step": i, "day": i // 24, "money": 3000.0 + i * 10} for i in range(n)]


def test_add_and_stats() -> None:
    buf = PrioritizedReplayBuffer(capacity=10)
    buf.add_many(_rows(5))
    stats = buf.stats()
    assert stats["n_rows"] == 5
    assert stats["n_episodes"] == 0


def test_capacity_evicts_oldest() -> None:
    buf = PrioritizedReplayBuffer(capacity=3)
    buf.add_many(_rows(5))
    steps = {r.data["step"] for r in buf.rows}
    assert steps == {2, 3, 4}


def test_sample_is_seeded_deterministic() -> None:
    a = PrioritizedReplayBuffer(capacity=100, seed=7)
    a.add_many(_rows(50))
    b = PrioritizedReplayBuffer(capacity=100, seed=7)
    b.add_many(_rows(50))
    assert [r.data["step"] for r in a.sample(10)] == [r.data["step"] for r in b.sample(10)]


def test_sample_respects_batch_size() -> None:
    buf = PrioritizedReplayBuffer(capacity=100, seed=7)
    buf.add_many(_rows(50))
    batch = buf.sample(8)
    assert len(batch) == 8


def test_high_priority_rows_float_up() -> None:
    buf = PrioritizedReplayBuffer(capacity=100, seed=1)
    base = [{"step": i, "money": 3000.0} for i in range(100)]
    base[0]["money_delta"] = 5000.0  # large money swing -> boosted priority
    buf.add_many(base)
    sample = buf.sample(40, replace=True)
    assert any(r.data["step"] == 0 for r in sample)  # high-priority row selected


def test_filter_keeps_matching_rows() -> None:
    buf = PrioritizedReplayBuffer(capacity=100)
    buf.add_many(_rows(10))
    kept = buf.filter(lambda r: r["day"] < 1)
    assert len(kept.rows) == 10


def test_to_json_roundtrip(tmp_path: Path) -> None:
    buf = PrioritizedReplayBuffer(capacity=50, seed=3)
    buf.add_many(_rows(10))
    path = tmp_path / "buffer.json"
    path.write_text(json.dumps(buf.to_json()), encoding="utf-8")
    loaded = PrioritizedReplayBuffer.from_json(json.loads(path.read_text()))
    assert loaded.stats()["n_rows"] == buf.stats()["n_rows"]
    assert loaded.episode_ids() == buf.episode_ids()


def test_clear() -> None:
    buf = PrioritizedReplayBuffer(capacity=50)
    buf.add_many(_rows(10))
    buf.clear()
    assert buf.stats()["n_rows"] == 0
