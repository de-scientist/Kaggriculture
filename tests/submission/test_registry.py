"""Tests for the Stage 4B registries and opponent suite."""

from __future__ import annotations

from agent.evaluation.opponents import build_opponent, opponent_profile
from agent.evaluation.registry import (
    Challenger,
    ChallengerRegistry,
    ChampionRegistry,
    ChampionVersion,
    Hypothesis,
    HypothesisRegistry,
)
from agent.submission.failsafe import FailSafeAgent


def test_build_opponent_builtins() -> None:
    assert build_opponent("random") == "random"
    assert build_opponent("starter") == "starter"


def test_build_opponent_presets_are_failsafe() -> None:
    for name in ("conservative", "aggressive", "expansion", "production", "market", "balanced"):
        assert isinstance(build_opponent(name), FailSafeAgent)


def test_build_opponent_unknown_raises() -> None:
    try:
        build_opponent("does-not-exist")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_opponent_profile_describes_behaviour() -> None:
    p = opponent_profile("aggressive")
    assert isinstance(p, str) and len(p) > 0


def test_champion_registry_record_and_current(tmp_path) -> None:
    reg = ChampionRegistry(tmp_path / "champ.json")
    reg.record(ChampionVersion(version="v1.0", commit="abc", config={}, notes="n"))
    reg.record(ChampionVersion(version="v1.1", commit="def", config={}, notes="n"))
    assert reg.current().version == "v1.1"
    assert len(reg.all()) == 2


def test_challenger_registry_decide(tmp_path) -> None:
    reg = ChallengerRegistry(tmp_path / "chall.json")
    reg.register(Challenger(candidate_id="C01", parent="v1.0", version="c01", hypothesis="h", commit="x", configuration={}))
    reg.record_result("C01", {"win_rate": 0.5})
    reg.decide("C01", "RETIRE", "weaker")
    assert reg.get("C01").decision == "RETIRE"
    assert reg.get("C01").results["decision_reason"] == "weaker"


def test_hypothesis_registry_update(tmp_path) -> None:
    reg = HypothesisRegistry(tmp_path / "hyp.json")
    reg.add(Hypothesis(id="H-A", date="d", hypothesis="h", reason="r", affected_component="c", expected_effect="e", experiment="x"))
    reg.update("H-A", "refuted", "RETIRE")
    assert reg.all()[0].decision == "RETIRE"
