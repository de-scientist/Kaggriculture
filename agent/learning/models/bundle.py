"""Learned model bundle consumed by the runtime hybrid/learned policies.

``agent.runtime.policies`` expects an object exposing:

* ``value.predict(x_scaled)`` — value estimate,
* ``policy.predict_proba(x_scaled)`` — action-type probabilities,
* ``scaler.transform(x_raw)`` — feature standardization,
* ``ood.is_ood(x_raw, threshold)`` — out-of-distribution flag,
* ``action_types`` — labels aligned with ``policy`` classes,
* ``is_ready()`` — whether a usable model is actually loaded.

The bundle is serialized to one JSON file so the dependency-free runtime can
load it without numpy/sklearn.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from ...runtime.constants import ANIMALS, CROPS
from ..features import FEATURE_NAMES, FEATURE_VERSION
from .ood import OODDetector
from .policy_model import SoftmaxPolicyModel
from .scaler import FeatureScaler
from .value_model import LinearValueModel


@dataclass
class LearnedBundle:
    """Container for a versioned set of learned artifacts."""

    value: LinearValueModel | None = None
    policy: SoftmaxPolicyModel | None = None
    scaler: FeatureScaler | None = None
    ood: OODDetector | None = None
    feature_version: int = FEATURE_VERSION
    feature_names: list[str] = field(default_factory=list)
    model_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def action_types(self) -> list[str]:
        return list(self.policy.classes) if self.policy is not None else []

    def is_ready(self) -> bool:
        """True when a usable, version-compatible model is loaded."""
        if self.feature_version != FEATURE_VERSION:
            return False
        if self.scaler is None or self.scaler.n_features == 0:
            return False
        if self.value is None and self.policy is None:
            return False
        if self.value is not None and self.value.n_features != self.scaler.n_features:
            return False
        if self.policy is not None and self.policy.n_features != self.scaler.n_features:
            return False
        return True

    @classmethod
    def placeholder(cls) -> LearnedBundle:
        """Empty bundle that ``is_ready()`` reports False (champion fallback)."""
        return cls(feature_version=-1)

    # -- persistence ------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": 1,
            "model_id": self.model_id,
            "feature_version": self.feature_version,
            "feature_names": self.feature_names or list(FEATURE_NAMES),
            "scaler": self.scaler.to_dict() if self.scaler is not None else None,
            "value": self.value.to_dict() if self.value is not None else None,
            "policy": self.policy.to_dict() if self.policy is not None else None,
            "ood": self.ood.to_dict() if self.ood is not None else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> LearnedBundle:
        scaler = FeatureScaler.from_dict(payload["scaler"]) if payload.get("scaler") else None
        value = LinearValueModel.from_dict(payload["value"]) if payload.get("value") else None
        policy = SoftmaxPolicyModel.from_dict(payload["policy"]) if payload.get("policy") else None
        ood = OODDetector.from_dict(payload["ood"]) if payload.get("ood") else None
        return cls(
            value=value,
            policy=policy,
            scaler=scaler,
            ood=ood,
            feature_version=int(payload.get("feature_version", FEATURE_VERSION)),
            feature_names=[str(n) for n in payload.get("feature_names", [])],
            model_id=str(payload.get("model_id", "")),
            metadata=dict(payload.get("metadata", {}) or {}),
        )

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, separators=(",", ":"))
            handle.write("\n")

    @classmethod
    def load(cls, path: str) -> LearnedBundle:
        with open(path, encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))


def default_action_types() -> list[str]:
    """Canonical action-type vocabulary for the champion's candidate tasks."""
    crop_ops = ["plant", "harvest", "water", "water_bonus", "dig"]
    animal_ops = ["feed", "care", "collect", "place", "build_pasture", "build_coop"]
    return crop_ops + animal_ops + ["pass", "move"]


def env_signature() -> dict[str, Any]:
    """Stable description of the environment constants the models assume."""
    return {
        "crops": {c: dict(spec) for c, spec in CROPS.items()},
        "animals": {a: dict(spec) for a, spec in ANIMALS.items()},
    }
