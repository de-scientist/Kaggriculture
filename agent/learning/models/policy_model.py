"""Multinomial logistic (softmax) policy model, pure-Python inference.

Predicts P(action_type | state) over the champion's candidate action types.
Fitted offline with L2-regularized gradient descent; ``predict_proba`` is a
dependency-free softmax.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any


class SoftmaxPolicyModel:
    """``predict_proba`` returns a softmax over class logits."""

    def __init__(
        self,
        classes: Sequence[str] | None = None,
        weights: Sequence[Sequence[float]] | None = None,
        bias: Sequence[float] | None = None,
    ) -> None:
        self.classes = [str(c) for c in classes] if classes is not None else []
        self.weights = [[float(v) for v in row] for row in weights] if weights is not None else []
        self.bias = [float(b) for b in bias] if bias is not None else []

    @property
    def n_classes(self) -> int:
        return len(self.classes)

    @property
    def n_features(self) -> int:
        return len(self.weights[0]) if self.weights else 0

    def _logits(self, x_scaled: Sequence[float]) -> list[float]:
        if len(x_scaled) != self.n_features:
            raise ValueError(
                "feature count mismatch: policy model expects "
                f"{self.n_features}, got {len(x_scaled)}"
            )
        logits: list[float] = []
        for row, bias in zip(self.weights, self.bias, strict=True):
            total = bias
            for w, value in zip(row, x_scaled, strict=True):
                total += w * float(value)
            logits.append(total)
        return logits

    def predict_proba(self, x_scaled: Sequence[float]) -> list[float]:
        """Softmax probabilities, one per class."""
        logits = self._logits(x_scaled)
        if not logits:
            return []
        peak = max(logits)
        exps = [math.exp(z - peak) for z in logits]
        total = sum(exps)
        return [e / total for e in exps]

    def predict(self, x_scaled: Sequence[float]) -> str | None:
        proba = self.predict_proba(x_scaled)
        if not proba:
            return None
        best = max(range(len(proba)), key=lambda i: proba[i])
        return self.classes[best] if best < len(self.classes) else None

    def to_dict(self) -> dict[str, Any]:
        return {"classes": self.classes, "weights": self.weights, "bias": self.bias}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SoftmaxPolicyModel:
        return cls(
            classes=payload.get("classes", []),
            weights=payload.get("weights", []),
            bias=payload.get("bias", []),
        )
