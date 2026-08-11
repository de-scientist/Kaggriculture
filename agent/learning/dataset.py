"""Episode dataset construction from experience logs.

Experiences are stored per-turn; this module groups them into episodes, joins
each episode's manifest metadata (opponent, seed, outcome), builds training
labels (value target = final bank, policy target = chosen action type), and
splits episodes into train/validation/test with strict no-leakage guarantees
(an episode appears in exactly one split).
"""

from __future__ import annotations

import json
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .schema import FEATURE_VERSION

_VALUE_TARGET_NAMES = ("final_money",)


@dataclass
class ExperienceEpisode:
    """One episode's rows plus manifest metadata."""

    episode_id: str
    rows: list[dict[str, Any]]
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def outcome(self) -> float:
        value = self.meta.get("outcome_money")
        if value is None and self.rows:
            value = self.rows[-1].get("state", {}).get("money")
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value))
        except (TypeError, ValueError):
            return 0.0

    def sorted_rows(self) -> list[dict[str, Any]]:
        return sorted(self.rows, key=lambda r: int(r.get("step", 0)))


def load_episodes(experiences_dir: str | Path) -> list[ExperienceEpisode]:
    """Load all episode JSONL files plus the manifest under ``experiences_dir``."""
    root = Path(experiences_dir)
    manifest: dict[str, dict[str, Any]] = {}
    manifest_path = root / "manifest.jsonl"
    if manifest_path.exists():
        with manifest_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:  # pragma: no cover - corrupt log
                    continue
                if isinstance(row, Mapping) and row.get("episode_id"):
                    manifest[str(row["episode_id"])] = dict(row)

    grouped: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(root.glob("*.jsonl")):
        if path.name == "manifest.jsonl":
            continue
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:  # pragma: no cover - corrupt log
                    continue
                if not isinstance(row, Mapping):
                    continue
                episode_id = str(row.get("episode_id", path.stem))
                grouped.setdefault(episode_id, []).append(dict(row))

    episodes = [
        ExperienceEpisode(
            episode_id=episode_id,
            rows=rows,
            meta=manifest.get(episode_id, {}),
        )
        for episode_id, rows in grouped.items()
        if rows
    ]
    episodes.sort(key=lambda e: e.episode_id)
    return episodes


def split_episodes(
    episodes: Sequence[ExperienceEpisode],
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 0,
) -> dict[str, list[ExperienceEpisode]]:
    """Deterministic episode-level split.  No episode appears in two splits."""
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-9:
        raise ValueError("split ratios must sum to 1.0")
    if not episodes:
        return {"train": [], "val": [], "test": []}
    rng = random.Random(seed)
    ordered = list(episodes)
    rng.shuffle(ordered)
    n_train = int(len(ordered) * train_ratio)
    n_val = int(len(ordered) * val_ratio)
    return {
        "train": ordered[:n_train],
        "val": ordered[n_train : n_train + n_val],
        "test": ordered[n_train + n_val :],
    }


@dataclass
class EpisodeDataset:
    """Flattened, labeled rows ready for the trainer."""

    features: list[list[float]]
    value_labels: list[float]
    policy_labels: list[str]
    episode_ids: list[str]
    steps: list[int]
    value_target: str = "final_money"
    feature_version: int = FEATURE_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.features)


def build_dataset(
    episodes: Sequence[ExperienceEpisode],
    feature_version: int = FEATURE_VERSION,
) -> EpisodeDataset:
    """Flatten episodes into labeled rows (value target = final bank)."""
    features: list[list[float]] = []
    value_labels: list[float] = []
    policy_labels: list[str] = []
    episode_ids: list[str] = []
    steps: list[int] = []
    for episode in episodes:
        outcome = episode.outcome
        for row in episode.sorted_rows():
            if int(row.get("feature_version", -1)) != feature_version:
                raise ValueError(
                    f"episode {episode.episode_id} has feature_version "
                    f"{row.get('feature_version')}, expected {feature_version}"
                )
            feats = row.get("features")
            if not isinstance(feats, list) or len(feats) == 0:
                raise ValueError(f"episode {episode.episode_id} has invalid features")
            features.append([float(v) for v in feats])
            value_labels.append(outcome)
            policy_labels.append(str(row.get("farmer_action_type", "pass")))
            episode_ids.append(episode.episode_id)
            steps.append(int(row.get("step", 0)))
    return EpisodeDataset(
        features=features,
        value_labels=value_labels,
        policy_labels=policy_labels,
        episode_ids=episode_ids,
        steps=steps,
        feature_version=feature_version,
        metadata={
            "n_episodes": len(episodes),
            "n_rows": len(features),
            "episodes": [e.episode_id for e in episodes],
        },
    )


def validate_no_leakage(splits: Mapping[str, Sequence[ExperienceEpisode]]) -> list[str]:
    """Return a list of violation descriptions (empty when clean)."""
    seen: dict[str, str] = {}
    violations: list[str] = []
    for split_name, episodes in splits.items():
        for episode in episodes:
            previous = seen.get(episode.episode_id)
            if previous is not None and previous != split_name:
                violations.append(
                    f"episode {episode.episode_id} appears in both {previous} and {split_name}"
                )
            seen[episode.episode_id] = split_name
    return violations


def dataset_summary(dataset: EpisodeDataset) -> dict[str, Any]:
    """Distribution summary used for validation and reports."""
    from collections import Counter

    action_counts = Counter(dataset.policy_labels)
    totals = {
        "rows": len(dataset),
        "episodes": len(set(dataset.episode_ids)),
        "value_min": min(dataset.value_labels) if dataset.value_labels else None,
        "value_max": max(dataset.value_labels) if dataset.value_labels else None,
        "value_mean": (
            (sum(dataset.value_labels) / len(dataset.value_labels))
            if dataset.value_labels
            else None
        ),
        "n_action_types": len(action_counts),
        "action_distribution": {k: v for k, v in sorted(action_counts.items())},
    }
    return totals
