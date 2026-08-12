"""Regression tests for previously discovered bugs (chapter 9 §183).

Each test documents a bug that was found and fixed, ensuring it never
returns silently.  A bug fixed once must never return.
"""

from __future__ import annotations

from typing import Any

from agent.decision import action_generator
from agent.decision.decision_context import DecisionContext
from agent.decision.decision_engine import decide
from agent.domain.position import Position
from agent.domain.tile import Tile
from agent.services import crop_service


class TestRegressionCropWatering:
    """Bug: watering a crop with an existing seed raised a ValueError instead of replacing it."""

    def test_water_replaces_existing_crop(self) -> None:
        tile = Tile(position=Position(0, 0))
        planted = crop_service.plant(tile, "WHEAT", day=0)
        watered = crop_service.water(planted)
        assert watered.crop is not None
        assert watered.crop.watered_today is True


class TestRegressionCropFertilizing:
    """Bug: fertilizing a planted crop raised a ValueError instead of replacing it."""

    def test_fertilize_replaces_existing_crop(self) -> None:
        tile = Tile(position=Position(0, 0))
        planted = crop_service.plant(tile, "WHEAT", day=0)
        fertilized = crop_service.fertilize(planted, day=0)
        assert fertilized.crop is not None
        assert fertilized.crop.fertilized_until_day == 3


class TestRegressionCropHarvest:
    """Bug: harvest called is_mature with wrong keyword argument."""

    def test_harvest_mature_crop_succeeds(self) -> None:
        tile = Tile(position=Position(0, 0))
        planted = crop_service.plant(tile, "WHEAT", day=0)
        watered = crop_service.water(planted)
        harvested = crop_service.harvest(watered, current_day=2)
        assert harvested.crop is not None
        assert harvested.crop.is_harvested is True


class TestRegressionInventoryRelease:
    """Bug: test_release_item tried to reserve from an empty inventory."""

    def test_release_restores_reserved_items(self) -> None:
        from agent.domain.inventory import Inventory
        from agent.services import inventory_service

        inv = Inventory()
        with_inv = inventory_service.add(inv, "WHEAT", 5)
        reserved = inventory_service.reserve(with_inv, "WHEAT", 2)
        assert inventory_service.available(reserved, "WHEAT") == 3
        result = inventory_service.release(reserved, "WHEAT", 2)
        assert inventory_service.available(result, "WHEAT") == 5


class TestRegressionDecisionFallbackMetrics:
    """Bug: decision_count metric was not incremented when the engine fell back to PASS on error."""

    def test_fallback_increments_decision_count(self) -> None:
        from agent.observability import get_metrics
        from tests.fixtures.observations import minimal_observation

        metrics = get_metrics()
        before = metrics.counter("decision_count")

        obs = minimal_observation()
        context = DecisionContext(obs=obs, player=0, step=1, day=0)

        def boom(_ctx: Any) -> Any:
            raise ValueError("test error")

        original = action_generator.generate_candidates
        action_generator.generate_candidates = boom
        try:
            action = decide(context)
        finally:
            action_generator.generate_candidates = original

        assert action["farmer"] == ["PASS"]
        assert metrics.counter("decision_count") == before + 1.0


class TestRegressionObservationHashDeterminism:
    """Bug: observation hashes were not deterministic across runs."""

    def test_hash_deterministic(self) -> None:
        from agent.observability.replay import observation_hash

        obs1 = {"player": 0, "step": 0, "day": 0}
        obs2 = {"player": 0, "step": 0, "day": 0}
        obs3 = {"player": 0, "step": 1, "day": 0}

        h1 = observation_hash(obs1)
        h2 = observation_hash(obs2)
        h3 = observation_hash(obs3)

        assert h1 == h2
        assert h1 != h3
