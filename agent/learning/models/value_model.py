"""Linear value model (pure-Python inference).

Predicts a scalar future-value target (e.g. final bank balance) from the
standardized feature vector.  Fitted offline as ridge regression.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


class LinearValueModel:
    """``predict(x_scaled) = b + sum(w_i * x_i)``."""

    def __init__(self, weights: Sequence[float] | None = None, bias: float = 0.0) -> None:
        self.weights = [float(w) for w in weights] if weights is not None else []
        self.bias = float(bias)

    @property
    def n_features(self) -> int:
        return len(self.weights)

    def predict(self, x_scaled: Sequence[float]) -> float:
        """Predict the target from a standardized feature vector."""
        if len(x_scaled) != self.n_features:
            raise ValueError(
                "feature count mismatch: value model expects "
                f"{self.n_features}, got {len(x_scaled)}"
            )
        total = self.bias
        for w, value in zip(self.weights, x_scaled, strict=True):
            total += w * float(value)
        return total

    def to_dict(self) -> dict[str, Any]:
        return {"weights": self.weights, "bias": self.bias}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> LinearValueModel:
        return cls(weights=payload.get("weights", []), bias=float(payload.get("bias", 0.0)))
