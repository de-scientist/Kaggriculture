"""Feature standardization with pure-Python transform.

Fitted offline on the training split; the runtime only ever calls
``transform``.  Statistics are stored per feature (mean / std), so the model
never silently consumes unscaled or differently-scaled features.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


class FeatureScaler:
    """Standard-scaler whose ``transform`` is dependency-free."""

    def __init__(
        self, means: Sequence[float] | None = None, stds: Sequence[float] | None = None
    ) -> None:
        self.means = [float(v) for v in means] if means is not None else []
        self.stds = [float(v) for v in stds] if stds is not None else []

    @property
    def n_features(self) -> int:
        return len(self.means)

    def fit(self, rows: Sequence[Sequence[float]]) -> FeatureScaler:
        """Compute mean/std over a list of feature vectors."""
        n = len(rows[0]) if rows else 0
        if n == 0:
            return self
        sums = [0.0] * n
        sumsq = [0.0] * n
        count = 0
        for row in rows:
            if len(row) != n:
                raise ValueError("inconsistent feature lengths in scaler fit")
            count += 1
            for i, value in enumerate(row):
                v = float(value)
                sums[i] += v
                sumsq[i] += v * v
        self.means = [s / count for s in sums]
        self.stds = []
        for i in range(n):
            mean = sums[i] / count
            var = max(0.0, sumsq[i] / count - mean * mean)
            self.stds.append(var**0.5)
        return self

    def transform(self, x: Sequence[float]) -> list[float]:
        """Standardize one feature vector (pure Python)."""
        if len(x) != self.n_features:
            raise ValueError(
                f"feature count mismatch: scaler expects {self.n_features}, got {len(x)}"
            )
        out: list[float] = []
        for i, value in enumerate(x):
            v = float(value)
            std = self.stds[i]
            if std and std > 1e-12:
                out.append((v - self.means[i]) / std)
            else:
                out.append(0.0)
        return out

    def to_dict(self) -> dict[str, Any]:
        return {"means": self.means, "stds": self.stds}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> FeatureScaler:
        return cls(means=payload.get("means", []), stds=payload.get("stds", []))
