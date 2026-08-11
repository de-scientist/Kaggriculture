"""Learned model artifacts: scaler, value, policy, OOD, and the bundle."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.learning.features import FEATURE_VERSION, build_features
from agent.learning.models.bundle import LearnedBundle, default_action_types, env_signature
from agent.learning.models.ood import OODDetector
from agent.learning.models.policy_model import SoftmaxPolicyModel
from agent.learning.models.scaler import FeatureScaler
from agent.learning.models.value_model import LinearValueModel
from agent.learning.schema import ACTION_TYPES
from agent.runtime.game import GameSnapshot
from tests.fixtures.observations import minimal_observation


def _features(n: int = 3) -> list[float]:
    snap = GameSnapshot.from_obs(minimal_observation())
    feats = build_features(snap)
    return [v * i for i in range(1, n + 1) for v in feats[:1]]


class TestFeatureScaler:
    def test_fit_transform_shape(self) -> None:
        scaler = FeatureScaler().fit([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        out = scaler.transform([3.0, 4.0])
        assert len(out) == 2
        assert out[0] == pytest.approx(0.0)  # mean of 1,3,5 is 3

    def test_zero_variance_does_not_crash(self) -> None:
        scaler = FeatureScaler().fit([[2.0, 1.0], [2.0, 1.0], [2.0, 1.0]])
        out = scaler.transform([2.0, 1.0])
        assert out == [0.0, 0.0]

    def test_dict_roundtrip(self) -> None:
        scaler = FeatureScaler().fit([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        restored = FeatureScaler.from_dict(scaler.to_dict())
        assert restored.transform([9.0, 9.0]) == scaler.transform([9.0, 9.0])


class TestLinearValueModel:
    def test_predict_linear(self) -> None:
        model = LinearValueModel(weights=[2.0, -1.0], bias=5.0)
        assert model.predict([3.0, 4.0]) == pytest.approx(7.0)

    def test_roundtrip(self) -> None:
        model = LinearValueModel(weights=[1.5, 2.5], bias=-2.0)
        restored = LinearValueModel.from_dict(model.to_dict())
        assert restored.predict([1.0, 1.0]) == model.predict([1.0, 1.0])


class TestSoftmaxPolicyModel:
    def test_proba_sums_to_one(self) -> None:
        model = SoftmaxPolicyModel(
            classes=["a", "b", "c"],
            weights=[[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]],
            bias=[0.0, 0.0, 0.0],
        )
        probs = model.predict_proba([1.0, 1.0])
        assert len(probs) == 3
        assert sum(probs) == pytest.approx(1.0)
        assert all(0.0 <= p <= 1.0 for p in probs)

    def test_roundtrip(self) -> None:
        model = SoftmaxPolicyModel(
            classes=["a", "b"], weights=[[1.0, 0.0], [0.0, 1.0]], bias=[0.1, -0.1]
        )
        restored = SoftmaxPolicyModel.from_dict(model.to_dict())
        assert restored.predict_proba([0.5, 0.5]) == pytest.approx(model.predict_proba([0.5, 0.5]))


class TestOODDetector:
    def test_in_distribution_is_not_ood(self) -> None:
        ood = OODDetector().fit([[1.0, 2.0], [2.0, 3.0], [1.5, 2.5]])
        assert not ood.is_ood([1.6, 2.4], threshold=2.25)

    def test_far_out_is_ood(self) -> None:
        ood = OODDetector().fit([[1.0, 2.0], [2.0, 3.0], [1.5, 2.5]])
        assert ood.is_ood([500.0, -300.0], threshold=2.25)

    def test_roundtrip(self) -> None:
        ood = OODDetector().fit([[1.0, 2.0], [2.0, 3.0]])
        restored = OODDetector.from_dict(ood.to_dict())
        assert restored.is_ood([100.0, 100.0], 2.25) == ood.is_ood([100.0, 100.0], 2.25)


class TestLearnedBundle:
    def _bundle(self) -> LearnedBundle:
        scaler = FeatureScaler().fit([[1.0, 0.0], [0.0, 1.0]])
        value = LinearValueModel(weights=[1.0, 1.0], bias=0.0)
        policy = SoftmaxPolicyModel(
            classes=["plant", "harvest"], weights=[[1.0, 0.0], [0.0, 1.0]], bias=[0.0, 0.0]
        )
        ood = OODDetector().fit([[1.0, 0.0], [0.0, 1.0]])
        return LearnedBundle(
            value=value,
            policy=policy,
            scaler=scaler,
            ood=ood,
            feature_version=FEATURE_VERSION,
            model_id="test-model",
        )

    def test_is_ready_with_all_components(self) -> None:
        assert self._bundle().is_ready()

    def test_placeholder_is_not_ready(self) -> None:
        assert not LearnedBundle.placeholder().is_ready()

    def test_feature_version_mismatch_not_ready(self) -> None:
        bundle = self._bundle()
        bundle.feature_version = FEATURE_VERSION + 1
        assert not bundle.is_ready()

    def test_action_types_from_policy(self) -> None:
        assert self._bundle().action_types == ["plant", "harvest"]

    def test_default_action_types_cover_champion(self) -> None:
        types = default_action_types()
        for action in ACTION_TYPES:
            assert action in types

    def test_env_signature_has_crops(self) -> None:
        sig = env_signature()
        assert "WHEAT" in sig["crops"]
        assert "GOOSE" in sig["animals"]

    def test_save_load_roundtrip(self, tmp_path: Path) -> None:
        bundle = self._bundle()
        path = tmp_path / "model.json"
        bundle.save(str(path))
        loaded = LearnedBundle.load(str(path))
        assert loaded.model_id == "test-model"
        assert loaded.is_ready()
        assert loaded.action_types == ["plant", "harvest"]
