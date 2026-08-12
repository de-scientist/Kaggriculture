"""Tests for the exception hierarchy (chapter: exceptions)."""

from __future__ import annotations

import pytest

from agent.exceptions import (
    AdapterError,
    AnimalError,
    CompatibilityError,
    ConfigurationError,
    CropError,
    KaggricultureError,
    MarketError,
    MissingFieldError,
    MovementError,
    ObservationError,
    ObservationParseError,
    PlanningError,
    SchemaValidationError,
    StrategyError,
    ValidationError,
    WorkerError,
)


def test_all_subclasses_extend_base() -> None:
    subclasses = [
        AdapterError,
        AnimalError,
        ConfigurationError,
        CompatibilityError,
        CropError,
        MarketError,
        MissingFieldError,
        MovementError,
        ObservationError,
        ObservationParseError,
        PlanningError,
        SchemaValidationError,
        StrategyError,
        ValidationError,
        WorkerError,
    ]
    for cls in subclasses:
        assert issubclass(cls, KaggricultureError)


def test_can_catch_all_with_base() -> None:
    with pytest.raises(KaggricultureError):
        raise CropError("bad crop")


def test_message_is_preserved() -> None:
    err = WorkerError("something broke")
    assert err.message == "something broke"
    assert "something broke" in str(err)


def test_context_is_captured() -> None:
    err = AnimalError("cow escaped", context={"turn": 128, "player": 0})
    assert err.context == {"turn": 128, "player": 0}
    assert "turn=128" in str(err)


def test_context_defaults_to_empty() -> None:
    err = PlanningError("no plan")
    assert err.context == {}
    assert str(err) == "no plan"


def test_with_context_enriches_copy() -> None:
    err = MarketError("price spike", context={"turn": 1})
    enriched = err.with_context(player=1, component="MarketService")
    assert isinstance(enriched, MarketError)
    assert enriched.message == "price spike"
    assert enriched.context == {"turn": 1, "player": 1, "component": "MarketService"}
    # original untouched
    assert err.context == {"turn": 1}


def test_with_context_preserves_chaining() -> None:
    try:
        try:
            raise ValueError("root cause")
        except ValueError as exc:
            raise PlanningError("plan failed") from exc
    except PlanningError as err:
        enriched = err.with_context(turn=5)
        assert enriched.__cause__ is err.__cause__
        assert enriched.__context__ is not None


def test_strategy_error_carries_context() -> None:
    err = StrategyError("timeout", context={"strategy": "utility", "elapsed_ms": 50})
    assert err.context["strategy"] == "utility"
    assert err.context["elapsed_ms"] == 50


def test_observation_parse_error_is_adapter_error() -> None:
    assert issubclass(ObservationParseError, AdapterError)
    assert issubclass(ObservationParseError, KaggricultureError)


def test_validation_error_is_kaggriculture_error() -> None:
    err = ValidationError("missing target")
    assert isinstance(err, KaggricultureError)
    assert err.message == "missing target"
