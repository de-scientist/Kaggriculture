"""Replay support (chapter 164).

Captures the information needed for complete replay / post-mortem analysis of
every decision turn:

* observation hash
* decision trace
* strategy scores
* selected action
* execution time

Replay support is essential for debugging, regression testing, optimization,
and competition analysis.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent.observability.tracing import Trace


def observation_hash(observation: dict[str, Any]) -> str:
    """Deterministic SHA-256 hash of a raw observation dict."""
    canonical = json.dumps(observation, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


@dataclass
class ReplayRecord:
    """A single decision turn recorded for replay analysis."""

    turn: int
    day: int
    hour: int
    player: int
    observation_hash: str
    decision_id: str
    correlation_id: str
    strategy_scores: dict[str, Any]
    selected_action: dict[str, Any]
    execution_time_ms: float
    trace: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn": self.turn,
            "day": self.day,
            "hour": self.hour,
            "player": self.player,
            "observation_hash": self.observation_hash,
            "decision_id": self.decision_id,
            "correlation_id": self.correlation_id,
            "strategy_scores": self.strategy_scores,
            "selected_action": self.selected_action,
            "execution_time_ms": self.execution_time_ms,
            "trace": self.trace,
            "context": self.context,
        }


class ReplayStore:
    """In-memory + on-disk store of decision replay records."""

    def __init__(self, *, enabled: bool = True, directory: str = "replays") -> None:
        self._enabled = enabled
        self._directory = Path(directory)
        self._records: list[ReplayRecord] = []

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def directory(self) -> Path:
        return self._directory

    def enable(self, enabled: bool = True) -> None:
        self._enabled = enabled

    def record(
        self,
        *,
        turn: int,
        day: int,
        hour: int,
        player: int,
        observation: dict[str, Any],
        trace: Trace | dict[str, Any] | None = None,
        strategy_scores: dict[str, Any] | None = None,
        selected_action: dict[str, Any],
        execution_time_ms: float,
        context: dict[str, Any] | None = None,
    ) -> ReplayRecord | None:
        if not self._enabled:
            return None
        record = ReplayRecord(
            turn=turn,
            day=day,
            hour=hour,
            player=player,
            observation_hash=observation_hash(observation),
            decision_id=(trace.decision_id if isinstance(trace, Trace) else ""),
            correlation_id=(trace.correlation_id if isinstance(trace, Trace) else ""),
            strategy_scores=strategy_scores or {},
            selected_action=selected_action,
            execution_time_ms=round(float(execution_time_ms), 3),
            trace=(trace.to_dict() if isinstance(trace, Trace) else dict(trace or {})),
            context=context or {},
        )
        self._records.append(record)
        return record

    def records(self) -> list[ReplayRecord]:
        return list(self._records)

    def find(self, turn: int | None = None, decision_id: str | None = None) -> list[ReplayRecord]:
        result = self._records
        if turn is not None:
            result = [r for r in result if r.turn == turn]
        if decision_id:
            result = [r for r in result if r.decision_id == decision_id]
        return list(result)

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "count": len(self._records),
            "records": [r.to_dict() for r in self._records],
        }

    def save(self, path: str | Path | None = None) -> Path:
        if path is None:
            self._directory.mkdir(parents=True, exist_ok=True)
            path = self._directory / "replay.json"
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
        return out

    @classmethod
    def load(cls, path: str | Path) -> ReplayStore:
        p = Path(path)
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        store = cls(enabled=data.get("enabled", True), directory=str(p.parent))
        for raw in data.get("records", []):
            store._records.append(
                ReplayRecord(
                    turn=raw["turn"],
                    day=raw["day"],
                    hour=raw["hour"],
                    player=raw["player"],
                    observation_hash=raw["observation_hash"],
                    decision_id=raw["decision_id"],
                    correlation_id=raw["correlation_id"],
                    strategy_scores=raw["strategy_scores"],
                    selected_action=raw["selected_action"],
                    execution_time_ms=raw["execution_time_ms"],
                    trace=raw.get("trace", {}),
                    context=raw.get("context", {}),
                )
            )
        return store

    def clear(self) -> None:
        self._records.clear()


_default_store: ReplayStore | None = None


def get_replay_store() -> ReplayStore:
    global _default_store
    if _default_store is None:
        _default_store = ReplayStore()
    return _default_store


def reset_replay_store(enabled: bool = True, directory: str = "replays") -> ReplayStore:
    global _default_store
    _default_store = ReplayStore(enabled=enabled, directory=directory)
    return _default_store
