"""Model registry: statuses, promotion, rollback, active selection."""

from __future__ import annotations

import pytest
from pathlib import Path

from agent.learning.model_registry import ModelRegistry
from agent.learning.models.bundle import LearnedBundle
from agent.learning.registry import active_bundle_path, load_latest_bundle, reset_bundle_cache


def _register_two(reg: ModelRegistry) -> list[str]:
    for mid, status in [("m1", "experimental"), ("m2", "experimental")]:
        reg.register(
            model_id=mid,
            status=status,
            feature_version=1,
            dataset_version="d1",
            metrics={"acc": 0.5},
            note="",
        )
    return ["m1", "m2"]


def test_register_and_list(tmp_path: Path) -> None:
    reg = ModelRegistry(tmp_path)
    _register_two(reg)
    entries = reg.list_models()
    assert {e.model_id for e in entries} == {"m1", "m2"}
    assert all(e.status == "experimental" for e in entries)


def test_active_prefers_champion(tmp_path: Path) -> None:
    reg = ModelRegistry(tmp_path)
    _register_two(reg)
    reg.set_status("m1", "challenger")
    reg.set_status("m2", "validated")
    active = reg.active()
    assert active is not None
    assert active.model_id == "m2"  # newest validated beats challenger


def test_set_status_promotes_to_champion_and_demotes_old(tmp_path: Path) -> None:
    reg = ModelRegistry(tmp_path)
    _register_two(reg)
    reg.set_status("m1", "champion")
    reg.set_status("m2", "champion")
    active = reg.active()
    assert active is not None
    assert active.model_id == "m2"
    deprecated = reg.get("m1")
    assert deprecated is not None
    assert deprecated.status == "deprecated"


def test_rollback_promotes_given_model_to_champion(tmp_path: Path) -> None:
    reg = ModelRegistry(tmp_path)
    _register_two(reg)
    reg.set_status("m1", "champion")
    reg.set_status("m2", "challenger")
    reg.rollback("m2")
    active = reg.active()
    assert active is not None
    assert active.model_id == "m2"
    deprecated = reg.get("m1")
    assert deprecated is not None
    assert deprecated.status == "deprecated"


def test_bundle_path(tmp_path: Path) -> None:
    reg = ModelRegistry(tmp_path)
    reg.register(model_id="m1", status="experimental", feature_version=1)
    path = reg.bundle_path("m1")
    assert path.name == "model.json"
    assert str(path).startswith(str(tmp_path))


def test_load_latest_bundle_placeholder_when_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import agent.learning.registry as registry_mod
    from agent.learning.models.bundle import LearnedBundle
    from agent.learning.registry import default_model_dir

    monkeypatch.setenv("KAG_RUNTIME_MODEL_DIR", str(tmp_path / "nope"))
    reset_bundle_cache()
    bundle = registry_mod.load_latest_bundle()
    assert isinstance(bundle, LearnedBundle)
    assert not bundle.is_ready()
    assert default_model_dir() == tmp_path / "nope"


def test_load_latest_bundle_after_promote(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("KAG_RUNTIME_MODEL_DIR", str(tmp_path))
    reg = ModelRegistry(tmp_path)
    reg.register(model_id="m1", status="experimental", feature_version=1)
    # write a real (minimal) bundle file so it can be loaded
    bundle = LearnedBundle(feature_version=-1, model_id="m1")
    bundle_path = reg.bundle_path("m1")
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle.save(str(bundle_path))
    reset_bundle_cache()
    loaded = load_latest_bundle()
    assert not loaded.is_ready()  # experimental not active -> placeholder
    reg.set_status("m1", "champion")
    reset_bundle_cache()
    loaded = load_latest_bundle()
    assert loaded.model_id == "m1"


def test_active_bundle_path_returns_none_when_inactive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("KAG_RUNTIME_MODEL_DIR", str(tmp_path))
    reg = ModelRegistry(tmp_path)
    reg.register(model_id="m1", status="experimental", feature_version=1)
    reset_bundle_cache()
    assert active_bundle_path() is None
