"""Stage 3 — Hybrid policy: learned model + economic champion + safety.

The hybrid strategy implements the uncertainty-aware compute hierarchy from the
Stage 3 master prompt:

    learned policy  (when confident & on-distribution)
            +
    Stage 2 economic champion  (fallback / low confidence)
            +
    economic sanity guardrails

Decision flow:

    1. Always score candidates with the Stage 2 champion (economic planner).
    2. Load the active learned bundle.  If it is missing, not ``is_ready()``,
       fails to produce features, or raises, the champion result is returned
       unchanged -- the learned system can never break play.
    3. When the state is out-of-distribution or the policy confidence is below
       ``confidence_threshold``, defer entirely to the champion.
    4. Otherwise blend the champion score (normalized) with the learned
       policy's probability for each candidate's action type.  The blend weight
       scales with confidence so higher-confidence states trust the learned
       policy more.
    5. Apply the economic sanity guardrail: any candidate whose estimated cost
       exceeds available capital is rejected (score -inf).

This keeps the Stage 2 champion as the always-available fallback (non
negotiable rule) while allowing validated learned components to influence
decisions where they are confident and on-distribution.
"""

from __future__ import annotations

from typing import Any

from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.learning.features import build_features
from agent.learning.registry import load_latest_bundle
from agent.runtime.game import GameSnapshot
from agent.strategies.economic_strategy import EconomicStrategy
from agent.strategies.strategy import ScoredAction, Strategy


class HybridStrategy(Strategy):
    """Combines a learned policy with the Stage 2 economic champion safely."""

    def __init__(
        self,
        confidence_threshold: float = 0.5,
        learned_weight: float = 0.6,
        ood_threshold: float = 3.5,
        champion: Strategy | None = None,
    ) -> None:
        self.confidence_threshold = confidence_threshold
        self.learned_weight = learned_weight
        self.ood_threshold = ood_threshold
        self._champion = champion if champion is not None else EconomicStrategy()
        self.last_decision: dict[str, Any] = {}

    def evaluate(
        self,
        context: DecisionContext,
        actions: list[CandidateAction],
    ) -> list[ScoredAction]:
        champion_scored = self._champion.evaluate(context, actions)
        if not actions:
            self.last_decision = {"mode": "empty", "confidence": 0.0, "learned_weight": 0.0}
            return champion_scored

        bundle = load_latest_bundle()
        if bundle is None or not bundle.is_ready():
            self.last_decision = {
                "mode": "champion",
                "reason": "no_ready_model",
                "confidence": 0.0,
            }
            return champion_scored

        features = self._features(context)
        if features is None:
            self.last_decision = {
                "mode": "champion",
                "reason": "feature_error",
                "confidence": 0.0,
            }
            return champion_scored

        try:
            scaled = bundle.scaler.transform(features)  # type: ignore[union-attr]
            proba = bundle.policy.predict_proba(scaled)  # type: ignore[union-attr]
            classes = list(bundle.policy.classes)  # type: ignore[union-attr]
        except Exception:
            self.last_decision = {
                "mode": "champion",
                "reason": "inference_error",
                "confidence": 0.0,
            }
            return champion_scored

        if not classes or not proba:
            return champion_scored

        ood = self._is_ood(bundle, features)
        confidence = max(proba)
        preferred_idx = max(range(len(proba)), key=lambda i: proba[i])
        preferred_type = classes[preferred_idx]

        if ood or confidence < self.confidence_threshold:
            self.last_decision = {
                "mode": "champion",
                "reason": "ood" if ood else "low_confidence",
                "confidence": confidence,
                "preferred_type": preferred_type,
            }
            return champion_scored

        champ_scores = [s.score for s in champion_scored if s.action.id in {a.id for a in actions}]
        champ_norm = self._softmax(champ_scores)
        available = self._available_money(context)
        alpha = self.learned_weight * confidence

        scored: list[ScoredAction] = []
        champ_iter = iter(champ_norm)
        for action in actions:
            base = next(champ_iter, 0.0)
            p = self._type_prob(proba, classes, action.action_type)
            score = (1.0 - alpha) * base + alpha * p
            if action.estimated_cost > available + 1e-6:
                score = float("-inf")
            scored.append(
                ScoredAction(
                    action,
                    score,
                    f"hybrid alpha={alpha:.2f} champ={base:.3f} policy={p:.3f}",
                )
            )

        scored.sort(key=lambda s: -s.score)
        self.last_decision = {
            "mode": "hybrid",
            "confidence": confidence,
            "learned_weight": alpha,
            "preferred_type": preferred_type,
            "available_money": available,
        }
        return scored

    # -- helpers ----------------------------------------------------------
    def _is_ood(self, bundle: Any, features: list[float]) -> bool:
        ood_model = bundle.ood
        if ood_model is None:
            return False
        try:
            return bool(ood_model.is_ood(features, self.ood_threshold))
        except Exception:
            return False

    def _features(self, context: DecisionContext) -> list[float] | None:
        try:
            snapshot = GameSnapshot.from_obs(context.obs)
            return build_features(snapshot)
        except Exception:
            return None

    def _available_money(self, context: DecisionContext) -> float:
        game_state = context.game_state
        if game_state is not None and hasattr(game_state, "available_money"):
            try:
                return float(game_state.available_money())
            except Exception:
                pass
        obs = context.obs or {}
        farms = obs.get("farms")
        if isinstance(farms, list) and len(farms) > context.player:
            money = farms[context.player].get("money")
            if isinstance(money, (int, float)):
                return float(money)
        return 3000.0

    @staticmethod
    def _type_prob(proba: list[float], classes: list[str], action_type: str) -> float:
        if action_type in classes:
            return proba[classes.index(action_type)]
        return 1.0 / (len(classes) + 1)

    @staticmethod
    def _softmax(values: list[float]) -> list[float]:
        if not values:
            return []
        peak = max(values)
        exps = [float("e") ** (v - peak) for v in values]
        total = sum(exps)
        if total == 0.0:
            return [1.0 / len(values)] * len(values)
        return [e / total for e in exps]
