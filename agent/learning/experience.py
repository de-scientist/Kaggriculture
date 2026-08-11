"""Experience collection for the learning layer.

The recorder is wired into the runtime agent (``agent.runtime.agent``) through
``RuntimeSettings(record_experience=True)``.  It stores one compact JSON row
per turn under ``<directory>/<episode_id>.jsonl`` plus a ``manifest.jsonl`` of
episode metadata (opponent, seed, outcome).  Storage is append-only and bounded
only by disk; use ``scripts/stage3/collect_episodes.py`` or the
:class:`PrioritizedReplayBuffer` to curate it.

Two usage modes are supported:

* **Managed** (data collection): call ``begin_episode`` / ``observe`` /
  ``end_episode`` explicitly so episode ids and metadata are controlled.
* **Auto** (production, when recording is enabled): ``observe`` alone detects
  episode boundaries from the step counter resetting and records outcomes from
  the final observed bank balance.
"""

from __future__ import annotations

import itertools
import json
import logging
import threading
import time
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ..runtime.game import GameSnapshot
from ..runtime.settings import RuntimeSettings
from ..runtime.tasks import Task
from .features import FEATURE_VERSION, build_features, compact_state
from .schema import EXPERIENCE_SCHEMA_VERSION

logger = logging.getLogger(__name__)

_SCHEMA = EXPERIENCE_SCHEMA_VERSION


def _json_safe(value: Any) -> Any:
    """Coerce a value into JSON-serializable primitives."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if value == value and value not in (float("inf"), float("-inf")) else None
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "__dataclass_fields__"):
        return {str(f): _json_safe(getattr(value, f)) for f in value.__dataclass_fields__}
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        return str(value)


class ExperienceStore:
    """Append-only JSONL storage for one episode plus a global manifest."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self.directory / "manifest.jsonl"
        self._lock = threading.Lock()

    def open_episode(self, episode_id: str) -> Path:
        return self.directory / f"{episode_id}.jsonl"

    def record(self, episode_id: str, row: dict[str, Any]) -> None:
        path = self.open_episode(episode_id)
        with self._lock:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, separators=(",", ":")) + "\n")

    def write_manifest_row(self, row: dict[str, Any]) -> None:
        with self._lock:
            with self._manifest_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, separators=(",", ":")) + "\n")


class ExperienceRecorder:
    """Per-turn recorder used by the runtime and the data-collection pipeline."""

    def __init__(self, directory: str | Path) -> None:
        self.store = ExperienceStore(directory)
        self._episode_id: str | None = None
        self._episode_meta: dict[str, Any] = {}
        self._prev_step: int | None = None
        self._rows = 0
        self._last_money: float = 0.0
        self._seq = itertools.count(1)

    # -- lifecycle --------------------------------------------------------
    def begin_episode(self, episode_id: str, meta: Mapping[str, Any] | None = None) -> None:
        """Start a managed episode.  Auto-finalizes any open episode first."""
        if self._episode_id is not None:
            self.end_episode()
        self._episode_id = episode_id
        self._episode_meta = dict(meta or {})
        self._prev_step = None
        self._rows = 0
        self._last_money = 0.0

    def end_episode(
        self, meta: Mapping[str, Any] | None = None, outcome: float | None = None
    ) -> None:
        """Finalize the open episode and write its manifest row."""
        if self._episode_id is None:
            return
        merged = dict(self._episode_meta)
        merged.update(meta or {})
        if outcome is None:
            outcome = merged.get("outcome_money", self._last_money)
            try:
                outcome = float(outcome)
            except (TypeError, ValueError):
                outcome = self._last_money
        merged.update(
            {
                "episode_id": self._episode_id,
                "rows": self._rows,
                "outcome_money": outcome,
                "finished_at": time.time(),
            }
        )
        self.store.write_manifest_row(merged)
        self._episode_id = None
        self._episode_meta = {}
        self._prev_step = None

    def _auto_begin(self, snapshot: GameSnapshot) -> None:
        step = snapshot.step
        if self._episode_id is not None:
            if self._prev_step is None or step > self._prev_step:
                return
            self.end_episode()
        self.begin_episode(f"auto-{int(time.time())}-{uuid.uuid4().hex[:8]}", {})

    # -- recording --------------------------------------------------------
    def observe(self, snapshot: GameSnapshot, plan: Any) -> None:
        """Record one turn.  ``plan`` is a runtime ``TurnPlan``."""
        self._auto_begin(snapshot)
        assert self._episode_id is not None

        info = getattr(plan, "info", {})
        adjustments = info.get("adjustments", {}) if isinstance(info, Mapping) else {}
        settings = info.get("settings")
        selected_crop = _selected_crop(snapshot, settings)

        row: dict[str, Any] = {
            "schema": _SCHEMA,
            "episode_id": self._episode_id,
            "step": snapshot.step,
            "day": snapshot.day,
            "hour": snapshot.hour,
            "feature_version": FEATURE_VERSION,
            "farmer_action_type": getattr(plan, "farmer_action_type", "pass"),
            "farmer_op": _first_op(getattr(plan, "farmer_op", None)),
            "hands_ops": [_first_op(op) for op in getattr(plan, "hands_ops", [])],
            "market_orders": _json_safe(getattr(plan, "market_orders", [])),
            "n_tasks": _safe_int(info.get("n_tasks")) if isinstance(info, Mapping) else 0,
            "n_jobs": _safe_int(info.get("n_jobs")) if isinstance(info, Mapping) else 0,
            "candidate_types": _candidate_types(getattr(plan, "candidates", [])),
            "selected_crop": selected_crop,
            "adjustments": _json_safe(adjustments),
            "state": compact_state(snapshot),
            "features": build_features(snapshot),
        }
        self.store.record(self._episode_id, row)
        self._rows += 1
        self._prev_step = snapshot.step
        self._last_money = snapshot.money()

    def close(self) -> None:
        if self._episode_id is not None:
            self.end_episode()


def _first_op(op: Any) -> str:
    if isinstance(op, (list, tuple)) and op:
        return str(op[0])
    return "pass"


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _candidate_types(tasks: Any) -> dict[str, int]:
    out: dict[str, int] = {}
    if not isinstance(tasks, (list, tuple)):
        return out
    for task in tasks:
        if isinstance(task, Task):
            out[task.action_type] = out.get(task.action_type, 0) + 1
    return out


def _selected_crop(snapshot: GameSnapshot, settings: Any) -> str | None:
    if not isinstance(settings, RuntimeSettings):
        return None
    try:
        from ..runtime.crops import best_crop

        found = best_crop(snapshot, settings)
        return str(found) if found is not None else None
    except Exception:  # pragma: no cover - best effort
        return None
