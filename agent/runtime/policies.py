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
from dataclasses import dataclass, replace
from typing import Any

from .crops import best_crop
from .game import GameSnapshot
from .settings import RuntimeSettings
from .tasks import Task

logger = logging.getLogger(__name__)

LEARNED_RANK_WEIGHT = 25.0
OOD_ADJUST_THRESHOLD = 2.25


class Policy:
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


@dataclass
class EndgamePolicy(ChampionPolicy):
    """Champion planner plus horizon-aware wind-down and liquidation.

    Early in the season this is identical to :class:`ChampionPolicy`.  As the
    season closes it progressively (a) stops land/animals/hiring, (b) stops
    planting crops that cannot mature, and (c) lets the existing market endgame
    logic liquidate the shed into coins.  This is the default submission policy
    and implements the Stage 4 endgame optimisation (horizon-dependent strategy
    switching) without changing any early-game behaviour.
    """

    name = "endgame"
    wind_down_day: int = 22
    endgame_day: int = 26

    def adjust(
        self, snapshot: GameSnapshot, settings: RuntimeSettings
    ) -> tuple[RuntimeSettings, dict[str, Any]]:
        base_settings, info = super().adjust(snapshot, settings)
        day = snapshot.day
        info["mode"] = "champion"
        if day >= self.endgame_day or snapshot.is_final_day():
            # Liquidate: no new planting, no expansion, shed is already sold by
            # the market endgame logic.  Keep hands only if they are free.
            adjusted = replace(
                base_settings,
                plant_enabled=False,
                enable_animals=False,
                target_hands=(0, 0, 0, 0),
                land_latest_day=(0, 0, 0),
                sell_min_ratio=min(1.0, base_settings.sell_min_ratio + 0.1),
            )
            info["mode"] = "endgame_liquidate"
            return adjusted, info
        if day >= self.wind_down_day:
            # Wind-down: stop buying land/animals and taper hiring, but keep
            # planting short crops for the remaining days.
            adjusted = replace(
                base_settings,
                enable_animals=False,
                land_latest_day=(0, 0, 0),
                target_hands=(2, 2, 2, 2),
            )
            info["mode"] = "endgame_wind_down"
            return adjusted, info
        return base_settings, info


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
            info["policy_probs"] = {
                at: float(p) for at, p in zip(bundle.action_types, probs, strict=True)
            }
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
        prob_by_type = {at: float(p) for at, p in zip(bundle.action_types, probs, strict=True)}
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
        prob_by_type = {at: float(p) for at, p in zip(bundle.action_types, probs, strict=True)}
        ranked = list(tasks)
        ranked.sort(
            key=lambda t: -(t.value * 2.0 + self.rank_weight * prob_by_type.get(t.action_type, 0.0))
        )
        return ranked


def make_policy(name: str | None, settings: RuntimeSettings) -> Policy:
    """Build the policy named by ``name`` (champion | learned | hybrid | auto).

    The submission default is :class:`ChampionPolicy` (the Stage 4B champion,
    ``champion-v1.1``).  Stage 4B competitive validation showed the pure
    champion strictly dominates the earlier :class:`EndgamePolicy` on both win
    rate and average coins (21/21 vs 20/21 across diverse opponents, ~+7% avg
    coins, and it no longer loses to the market-oriented opponent).  The
    :class:`EndgamePolicy` wind-down/liquidation is retained under the
    ``"endgame"`` name for ablation experiments only.
    """
    if name is None or name in ("champion", "auto"):
        return ChampionPolicy()
    if name == "endgame":
        return EndgamePolicy()
    if name == "learned":
        return LearnedPolicy()
    if name == "hybrid":
        return HybridPolicy()
    if name == "hmarket1":
        return HMarket1Policy()
    return ChampionPolicy()


@dataclass
class _MelonProfile:
    """Concrete settings for one H-MARKET-1 melon allocation level."""

    melon_max_tiles: int
    melon_start_day: int
    melon_opp_gate: int
    melon_sell_cap: int
    sell_min_ratio: float
    endgame_sell_day: int


_MELON_PROFILES: dict[str, _MelonProfile] = {
    # Champion v1.1 defaults — used so the "baseline" profile reproduces the
    # frozen champion exactly when wrapped by HMarket1Policy.
    "baseline": _MelonProfile(8, 6, 3, 3, 0.85, 26),
    # Modest melon increase; still yields to opponent melon floods.
    "low": _MelonProfile(12, 5, 8, 4, 0.80, 26),
    # Substantial melon increase; contests the opponent instead of surrendering.
    "medium": _MelonProfile(16, 4, 99, 5, 0.75, 25),
    # Aggressive melon allocation; still keeps wheat/carrot as the staple floor.
    "high": _MelonProfile(20, 3, 99, 6, 0.70, 24),
}


class HMarket1Policy(ChampionPolicy):
    """H-MARKET-1 controlled challenger.

    Tests the hypothesis that contesting the high-value melon crop (instead of
    surrendering it when the opponent floods the market) and aligning melon
    maturity with the Day 26–29 liquidation window improves the win rate against
    the deterministic ``market`` opponent, without destroying the staple economy
    that already builds the mid-game lead.

    This policy reuses the entire champion planner and only overrides
    :class:`RuntimeSettings` via :meth:`adjust` — it does not duplicate the
    production system, and with ``melon_profile="baseline"`` / ``fertilizer_mode=
    "off"`` it is behaviourally identical to :class:`ChampionPolicy`.
    """

    name = "hmarket1"

    def __init__(
        self,
        melon_profile: str = "medium",
        fertilizer_mode: str = "off",
    ) -> None:
        self.melon_profile = melon_profile
        self.fertilizer_mode = fertilizer_mode
        self._profile = _MELON_PROFILES[melon_profile]

    def adjust(
        self, snapshot: GameSnapshot, settings: RuntimeSettings
    ) -> tuple[RuntimeSettings, dict[str, Any]]:
        base_settings, info = super().adjust(snapshot, settings)
        p = self._profile
        day = snapshot.day
        info["mode"] = "hmarket1_prod"
        info["melon_profile"] = self.melon_profile
        info["fertilizer_mode"] = self.fertilizer_mode

        overrides: dict[str, Any] = dict(
            melon_max_tiles=p.melon_max_tiles,
            melon_start_day=p.melon_start_day,
            melon_opp_gate=p.melon_opp_gate,
            melon_sell_cap=p.melon_sell_cap,
            sell_min_ratio=p.sell_min_ratio,
            endgame_sell_day=p.endgame_sell_day,
        )
        if self.fertilizer_mode == "melon":
            overrides["enable_fertilizer"] = True
            overrides["fertilizer_target_crop"] = "MELON"
            overrides["fertilizer_buy_threshold"] = 2
        elif self.fertilizer_mode == "aggressive":
            overrides["enable_fertilizer"] = True
            overrides["fertilizer_target_crop"] = "MELON"
            overrides["fertilizer_buy_threshold"] = 4

        # Endgame liquidation: from endgame_sell_day onward, sell everything we
        # can (the planner already sells all melon at endgame; this also lowers
        # the general sell threshold so high-value stock clears before the clock).
        if day >= p.endgame_sell_day or snapshot.is_final_day():
            overrides["sell_min_ratio"] = min(0.6, p.sell_min_ratio)
            overrides["melon_sell_cap"] = 50
            overrides["plant_enabled"] = False
            info["mode"] = "hmarket1_liquidate"
        elif day >= p.endgame_sell_day - 3:
            # Pre-liquidation wind-down: stop expanding, keep short staples only.
            overrides["land_latest_day"] = (0, 0, 0)
            overrides["target_hands"] = (2, 2, 2, 2)
            info["mode"] = "hmarket1_wind_down"

        return replace(base_settings, **overrides), info
