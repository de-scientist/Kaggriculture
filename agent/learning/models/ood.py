"""Out-of-distribution detection for the learned layer.

The detector is fitted on the training distribution and measures how far a
live feature vector is from it.  ``is_ood(feats, threshold)`` returns True when
the state is unlike anything the models were trained on, so the runtime can
degrade to the champion planner instead of trusting a possibly-miscalibrated
model on unseen territory.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


class OODDetector:
    """Distance-based OOD detector (mean absolute standardized deviation)."""

    def __init__(
        self,
        means: Sequence[float] | None = None,
        stds: Sequence[float] | None = None,
        train_distance: float = 0.0,
    ) -> None:
        self.means = [float(v) for v in means] if means is not None else []
        self.stds = [float(v) for v in stds] if stds is not None else []
        self.train_distance = float(train_distance)

    @property
    def n_features(self) -> int:
        return len(self.means)

    def fit(self, rows: Sequence[Sequence[float]]) -> OODDetector:
        """Fit on training features and record the reference distance."""
        n = len(rows[0]) if rows else 0
        if n == 0:
            return self
        sums = [0.0] * n
        sumsq = [0.0] * n
        count = 0
        for row in rows:
            if len(row) != n:
                raise ValueError("inconsistent feature lengths in OOD fit")
            count += 1
            for i, value in enumerate(row):
                v = float(value)
                sums[i] += v
                sumsq[i] += v * v
        means = [s / count for s in sums]
        stds: list[float] = []
        for i in range(n):
            mean = sums[i] / count
            var = max(0.0, sumsq[i] / count - mean * mean)
            stds.append(var**0.5)
        self.means = means
        self.stds = stds

        distances = [self.distance(row) for row in rows]
        self.train_distance = sum(distances) / len(distances) if distances else 0.0
        return self

    def distance(self, x: Sequence[float]) -> float:
        """Mean absolute standardized deviation (0 = on-distribution)."""
        if len(x) != self.n_features:
            raise ValueError(
                f"feature count mismatch: OOD detector expects {self.n_features}, got {len(x)}"
            )
        if not self.means:
            return 0.0
        total = 0.0
        for i, value in enumerate(x):
            std = self.stds[i]
            if std and std > 1e-12:
                total += abs((float(value) - self.means[i]) / std)
        return total / self.n_features

    def is_ood(self, x: Sequence[float], threshold: float) -> bool:
        """True when the state is far outside the training distribution."""
        if not self.means:
            return False
        d = self.distance(x)
        if d > threshold:
            return True
        max_z = 0.0
        for i, value in enumerate(x):
            std = self.stds[i]
            if std and std > 1e-12:
                z = abs((float(value) - self.means[i]) / std)
                if z > max_z:
                    max_z = z
        return max_z > 3.5

    def to_dict(self) -> dict[str, Any]:
        return {
            "means": self.means,
            "stds": self.stds,
            "train_distance": self.train_distance,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> OODDetector:
        return cls(
            means=payload.get("means", []),
            stds=payload.get("stds", []),
            train_distance=float(payload.get("train_distance", 0.0)),
        )
