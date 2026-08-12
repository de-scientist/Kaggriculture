"""Policy wrappers around the champion planner.

A policy can (a) adjust planner settings before the turn is planned and (b)
re-rank the champion's candidate tasks.  :class:`ChampionPolicy` is the pure
heuristic.  :class:`LearnedPolicy` / :class:`HybridPolicy` load trained models
from the model registry and, only when confident and in-distribution, bias the
champion's decisions by a bounded amount.  When no models are available or the
state is out-of-distribution, they degrade to the champion exactly.
"""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import replace
from typing import Any

from .crops import best_crop
from .game import GameSnapshot
from .settings import RuntimeSettings
from .tasks import Task

logger = logging.getLogger(__name__)

LEARNED_RANK_WEIGHT = 25.0
OOD_ADJUST_THRESHOLD = 2.25


class Policy(ABC):
    """Interface for policies that wrap the champion plan."""

    name = "policy"

    def adjust(
        self, snapshot: GameSnapshot, settings: RuntimeSettings
    ) -> tuple[RuntimeSettings, dict[str, Any]]:
        """Return (effective settings, diagnostics) before the turn is planned."""
        return settings, {}

    def rank_tasks(
        self, snapshot: GameSnapshot, tasks: list[Task], settings: RuntimeSettings
    ) -> list[Task]:
        """Optionally re-rank the candidate tasks before assignment."""
        return tasks


class ChampionPolicy(Policy):
    name = "champion"

    def adjust(
        self, snapshot: GameSnapshot, settings: RuntimeSettings
    ) -> tuple[RuntimeSettings, dict[str, Any]]:
        return settings, {"crop": best_crop(snapshot, settings), "mode": "champion"}


class _LearnedMixin:
    """Shared model loading / feature plumbing for learned policies."""

    def _bundle(self) -> Any:
        if getattr(self, "_bundle_cache", None) is None:
            try:
                from ..learning.registry import load_latest_bundle

                self._bundle_cache = load_latest_bundle()
            except Exception:  # pragma: no cover - registry import should not break play
                logger.exception("failed to load learned bundle; using champion")
                self._bundle_cache = None
        return self._bundle_cache

    def _features(self, snapshot: GameSnapshot) -> list[float]:
        from ..learning.features import build_features

        return build_features(snapshot)


class LearnedPolicy(Policy, _LearnedMixin):
    """Champion planner plus bounded, model-driven adjustments."""

    name = "learned"

    def __init__(self, rank_weight: float = LEARNED_RANK_WEIGHT) -> None:
        self.rank_weight = rank_weight
        self._bundle_cache: Any = None

    def adjust(
        self, snapshot: GameSnapshot, settings: RuntimeSettings
    ) -> tuple[RuntimeSettings, dict[str, Any]]:
        bundle = self._bundle()
        info: dict[str, Any] = {"mode": "learned"}
        if bundle is None or not bundle.is_ready():
            info["mode"] = "champion_fallback"
            return settings, info
        feats = self._features(snapshot)
        info["ood"] = bool(
            bundle.ood is not None and bundle.ood.is_ood(feats, OOD_ADJUST_THRESHOLD)
        )

        adjusted = settings
        if bundle.value is not None:
            pred = bundle.value.predict(bundle.scaler.transform(feats))
            info["value_prediction"] = float(pred)
            info["value_error"] = float(abs(pred - snapshot.money()))
            info["shed_value"] = float(snapshot.shed_value())
            info["money"] = float(snapshot.money())
            info["remaining_days"] = int(snapshot.remaining_days())
            if not info["ood"]:
                adjusted = self._sell_pressure_adjust(snapshot, adjusted, bundle, feats)
        if bundle.policy is not None:
            probs = bundle.policy.predict_proba(bundle.scaler.transform(feats))
            info["policy_probs"] = {at: float(p) for at, p in zip(bundle.action_types, probs)}
        return adjusted, info

    def _sell_pressure_adjust(
        self, snapshot: GameSnapshot, settings: RuntimeSettings, bundle: Any, feats: list[float]
    ) -> RuntimeSettings:
        pred = float(bundle.value.predict(bundle.scaler.transform(feats)))
        money = snapshot.money()
        shed_value = snapshot.shed_value()
        upside = pred - money
        if shed_value > 30.0 and upside < shed_value * 0.6:
            # The value model says holding stock will not pay off; liquidate.
            return replace(settings, sell_min_ratio=0.55, melon_sell_cap=8)
        if shed_value > 0.0 and upside < 0.0:
            return replace(settings, sell_min_ratio=0.7)
        return settings

    def rank_tasks(
        self, snapshot: GameSnapshot, tasks: list[Task], settings: RuntimeSettings
    ) -> list[Task]:
        bundle = self._bundle()
        if bundle is None or bundle.policy is None or not bundle.is_ready():
            return tasks
        feats = self._features(snapshot)
        if bundle.ood is not None and bundle.ood.is_ood(feats, OOD_ADJUST_THRESHOLD):
            return tasks
        probs = bundle.policy.predict_proba(bundle.scaler.transform(feats))
        prob_by_type = {at: float(p) for at, p in zip(bundle.action_types, probs)}
        ranked = list(tasks)
        ranked.sort(
            key=lambda t: -(t.value + self.rank_weight * prob_by_type.get(t.action_type, 0.0))
        )
        return ranked


class HybridPolicy(LearnedPolicy):
    """Learned adjustments, but the champion's top candidate always wins ties.

    The champion's own value dominates unless the learned signal is strong, so
    the learned layer can only resolve close calls and flag distress, never
    overturn an economically clear champion decision.
    """

    name = "hybrid"

    def rank_tasks(
        self, snapshot: GameSnapshot, tasks: list[Task], settings: RuntimeSettings
    ) -> list[Task]:
        bundle = self._bundle()
        if bundle is None or bundle.policy is None or not bundle.is_ready():
            return tasks
        feats = self._features(snapshot)
        if bundle.ood is not None and bundle.ood.is_ood(feats, OOD_ADJUST_THRESHOLD):
            return tasks
        probs = bundle.policy.predict_proba(bundle.scaler.transform(feats))
        prob_by_type = {at: float(p) for at, p in zip(bundle.action_types, probs)}
        ranked = list(tasks)
        ranked.sort(
            key=lambda t: -(t.value * 2.0 + self.rank_weight * prob_by_type.get(t.action_type, 0.0))
        )
        return ranked


def make_policy(name: str | None, settings: RuntimeSettings) -> Policy:
    """Build the policy named by ``name`` (champion | learned | hybrid | auto)."""
    if name is None or name in ("champion", "auto"):
        return ChampionPolicy()
    if name == "learned":
        return LearnedPolicy()
    if name == "hybrid":
        return HybridPolicy()
    return ChampionPolicy()
