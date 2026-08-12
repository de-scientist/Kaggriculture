"""Registries for Stage 4B championship governance.

Tracks the frozen Champion lineage, challenger candidates (with their
evidence-based promotion/retirement decisions), and the hypothesis register.
All state is persisted as JSON under ``artifacts/championship/`` so results are
reproducible and never silently overwritten.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

CHAMPIONSHIP_DIR = Path("artifacts/championship")


def _ensure_dir() -> Path:
    CHAMPIONSHIP_DIR.mkdir(parents=True, exist_ok=True)
    return CHAMPIONSHIP_DIR


@dataclass
class ChampionVersion:
    version: str
    commit: str
    config: dict[str, Any]
    notes: str = ""
    frozen_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Challenger:
    candidate_id: str
    parent: str
    version: str
    hypothesis: str
    commit: str
    configuration: dict[str, Any]
    changed_params: list[str] = field(default_factory=list)
    expected_outcome: str = ""
    results: dict[str, Any] = field(default_factory=dict)
    decision: str = ""  # PROMOTE | RETAIN | RETIRE

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Hypothesis:
    id: str
    date: str
    hypothesis: str
    reason: str
    affected_component: str
    expected_effect: str
    experiment: str
    metrics: str = ""
    result: str = ""
    decision: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class _JsonStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _load(self, default: Any) -> Any:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return default
        return default

    def _save(self, data: Any) -> None:
        _ensure_dir()
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


class ChampionRegistry(_JsonStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or (_ensure_dir() / "champion_registry.json"))
        self._versions: list[ChampionVersion] = [
            ChampionVersion(**v) for v in self._load([])
        ]

    def record(self, version: ChampionVersion) -> None:
        self._versions.append(version)
        self._save([v.to_dict() for v in self._versions])

    def all(self) -> list[ChampionVersion]:
        return list(self._versions)

    def current(self) -> ChampionVersion | None:
        return self._versions[-1] if self._versions else None


class ChallengerRegistry(_JsonStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or (_ensure_dir() / "challenger_registry.json"))
        self._items: dict[str, Challenger] = {
            c["candidate_id"]: Challenger(**c) for c in self._load([])
        }

    def register(self, challenger: Challenger) -> None:
        self._items[challenger.candidate_id] = challenger
        self._save([c.to_dict() for c in self._items.values()])

    def record_result(self, candidate_id: str, results: dict[str, Any]) -> None:
        if candidate_id in self._items:
            self._items[candidate_id].results = results
            self._save([c.to_dict() for c in self._items.values()])

    def decide(self, candidate_id: str, decision: str, reason: str = "") -> None:
        if candidate_id in self._items:
            self._items[candidate_id].decision = decision
            if reason:
                self._items[candidate_id].results.setdefault("decision_reason", reason)
            self._save([c.to_dict() for c in self._items.values()])

    def get(self, candidate_id: str) -> Challenger | None:
        return self._items.get(candidate_id)

    def all(self) -> list[Challenger]:
        return list(self._items.values())


class HypothesisRegistry(_JsonStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or (_ensure_dir() / "hypothesis_registry.json"))
        self._items: dict[str, Hypothesis] = {
            h["id"]: Hypothesis(**h) for h in self._load([])
        }

    def add(self, hypothesis: Hypothesis) -> None:
        self._items[hypothesis.id] = hypothesis
        self._save([h.to_dict() for h in self._items.values()])

    def update(self, hypothesis_id: str, result: str, decision: str) -> None:
        if hypothesis_id in self._items:
            self._items[hypothesis_id].result = result
            self._items[hypothesis_id].decision = decision
            self._save([h.to_dict() for h in self._items.values()])

    def all(self) -> list[Hypothesis]:
        return list(self._items.values())
