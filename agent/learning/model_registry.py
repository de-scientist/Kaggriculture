"""Model registry: versioned, statused model artifacts.

Every trained bundle is registered with a status that drives deployment:

* ``experimental`` — just trained, not yet validated.
* ``validated`` — passed offline evaluation on held-out episodes.
* ``challenger`` — validated and selected for champion/challenger testing.
* ``champion`` — the currently deployed model (or the active bundle).
* ``rejected`` — evaluated and dropped.
* ``deprecated`` — previously deployed, superseded.

Only one entry may be ``champion``; the runtime loader picks it.
"""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

STATUSES = ("experimental", "validated", "challenger", "champion", "rejected", "deprecated")


@dataclass
class ModelEntry:
    model_id: str
    status: str = "experimental"
    feature_version: int = 1
    dataset_version: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    note: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "status": self.status,
            "feature_version": self.feature_version,
            "dataset_version": self.dataset_version,
            "metrics": self.metrics,
            "note": self.note,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ModelEntry:
        return cls(
            model_id=str(payload.get("model_id", "")),
            status=str(payload.get("status", "experimental")),
            feature_version=int(payload.get("feature_version", 1)),
            dataset_version=str(payload.get("dataset_version", "")),
            metrics=dict(payload.get("metrics", {}) or {}),
            note=str(payload.get("note", "")),
            created_at=float(payload.get("created_at", time.time())),
        )


class ModelRegistry:
    """Persistent registry backed by ``<root>/manifest.json``."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self.root / "manifest.json"
        self._entries: dict[str, ModelEntry] = {}
        self._load()

    def _load(self) -> None:
        if not self._manifest_path.exists():
            return
        try:
            payload = json.loads(self._manifest_path.read_text(encoding="utf-8"))
            for raw in payload.get("entries", []):
                entry = ModelEntry.from_dict(raw)
                self._entries[entry.model_id] = entry
        except (json.JSONDecodeError, OSError):  # pragma: no cover - corrupt manifest
            return

    def _save(self) -> None:
        ordered = sorted(self._entries.values(), key=lambda e: e.created_at)
        payload = {"entries": [e.to_dict() for e in ordered]}
        self._manifest_path.write_text(
            json.dumps(payload, indent=2, separators=(",", ": ")) + "\n", encoding="utf-8"
        )

    # -- queries ----------------------------------------------------------
    def get(self, model_id: str) -> ModelEntry | None:
        return self._entries.get(model_id)

    def list_models(self) -> list[ModelEntry]:
        return sorted(self._entries.values(), key=lambda e: e.created_at, reverse=True)

    def bundle_path(self, model_id: str) -> Path:
        return self.root / model_id / "model.json"

    def active(self) -> ModelEntry | None:
        """Champion if present, else the newest validated/challenger entry."""
        champions = [e for e in self._entries.values() if e.status == "champion"]
        if champions:
            return max(champions, key=lambda e: e.created_at)
        candidates = [e for e in self._entries.values() if e.status in ("validated", "challenger")]
        if candidates:
            return max(candidates, key=lambda e: e.created_at)
        return None

    # -- mutations --------------------------------------------------------
    def register(
        self,
        model_id: str,
        status: str = "experimental",
        feature_version: int = 1,
        dataset_version: str = "",
        metrics: Mapping[str, Any] | None = None,
        note: str = "",
    ) -> ModelEntry:
        if status not in STATUSES:
            raise ValueError(f"invalid status {status!r}; must be one of {STATUSES}")
        if status == "champion":
            for existing in self._entries.values():
                if existing.status == "champion":
                    existing.status = "deprecated"
        entry = ModelEntry(
            model_id=model_id,
            status=status,
            feature_version=feature_version,
            dataset_version=dataset_version,
            metrics=dict(metrics or {}),
            note=note,
        )
        self._entries[model_id] = entry
        self._save()
        return entry

    def set_status(self, model_id: str, status: str) -> ModelEntry | None:
        entry = self._entries.get(model_id)
        if entry is None:
            return None
        if status not in STATUSES:
            raise ValueError(f"invalid status {status!r}; must be one of {STATUSES}")
        if status == "champion":
            for existing in self._entries.values():
                if existing.status == "champion" and existing.model_id != model_id:
                    existing.status = "deprecated"
        entry.status = status
        self._save()
        return entry

    def rollback(self, model_id: str) -> ModelEntry | None:
        """Demote the current champion and promote ``model_id`` if it exists."""
        entry = self._entries.get(model_id)
        if entry is None:
            return None
        self.set_status(model_id, "champion")
        return entry

    def to_json(self) -> str:
        return json.dumps([e.to_dict() for e in self.list_models()], separators=(",", ":"))
