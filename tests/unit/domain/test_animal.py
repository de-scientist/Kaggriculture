"""Unit tests for the Animal domain model (chapter 9)."""
from __future__ import annotations

import pytest

from agent.domain.animal import Animal


class TestAnimalConstruction:
    def test_defaults(self) -> None:
        animal = Animal(animal_type="GOOSE")
        assert animal.animal_type == "GOOSE"
        assert animal.hunger == 0
        assert animal.health == 100
        assert animal.fed_today is False
        assert animal.is_alive is True
        assert animal.is_escaped is False

    def test_custom_housing(self) -> None:
        animal = Animal(animal_type="COW", housing="PASTURE")
        assert animal.housing == "PASTURE"


class TestAnimalFeeding:
    def test_feed_marks_fed(self) -> None:
        animal = Animal(animal_type="GOOSE")
        fed = animal.feed()
        assert fed.fed_today is True
        assert fed.consecutive_unfed == 0

    def test_feed_already_fed_allows_again(self) -> None:
        animal = Animal(animal_type="GOOSE")
        fed = animal.feed()
        assert fed.fed_today is True

    def test_skip_feed_increments_hunger(self) -> None:
        animal = Animal(animal_type="GOOSE")
        skipped = animal.skip_feed()
        assert skipped.fed_today is False
        assert skipped.consecutive_unfed == 1
        assert skipped.hunger == 1


class TestAnimalEscaping:
    def test_two_consecutive_missed_feeds_escapes(self) -> None:
        animal = Animal(animal_type="GOOSE")
        skipped1 = animal.skip_feed()
        assert skipped1.is_escaped is False
        skipped2 = skipped1.skip_feed()
        assert skipped2.is_escaped is True

    def test_feed_resets_consecutive_unfed(self) -> None:
        animal = Animal(animal_type="GOOSE")
        skipped = animal.skip_feed()
        fed = skipped.feed()
        assert fed.consecutive_unfed == 0

    def test_feed_escaped_animal_raises(self) -> None:
        animal = Animal(animal_type="GOOSE")
        escaped = animal.skip_feed().skip_feed()
        assert escaped.is_escaped is True
        with pytest.raises(ValueError, match="escaped"):
            escaped.feed()


class TestAnimalProduction:
    def test_produce_without_feed_raises(self) -> None:
        animal = Animal(animal_type="GOOSE")
        with pytest.raises(ValueError, match="fed before producing"):
            animal.produce()

    def test_produce_with_feed_returns_no_bonus(self) -> None:
        animal = Animal(animal_type="GOOSE")
        fed = animal.feed()
        result, bonus = fed.produce()
        assert bonus == 0

    def test_produce_with_feed_and_care_returns_bonus(self) -> None:
        animal = Animal(animal_type="GOOSE")
        cared = animal.feed().care()
        result, bonus = cared.produce()
        assert bonus == 1

    def test_produce_clears_care_bonus(self) -> None:
        animal = Animal(animal_type="GOOSE")
        cared = animal.feed().care()
        result, bonus = cared.produce()
        assert result.pending_care_bonus == 0
        assert result.cared_today is False


class TestAnimalFertilizer:
    def test_collect_fertilizer_not_available_raises(self) -> None:
        animal = Animal(animal_type="GOOSE")
        fed = animal.feed()
        with pytest.raises(ValueError, match="No fertilizer"):
            fed.collect_fertilizer()

    def test_can_collect_fertilizer_after_production(self) -> None:
        animal = Animal(animal_type="GOOSE")
        fed = animal.feed()
        produced, _ = fed.produce()
        assert produced.fertilizer_available is True

    def test_collect_fertilizer_returns_one(self) -> None:
        animal = Animal(animal_type="GOOSE")
        fed = animal.feed()
        produced, _ = fed.produce()
        result, amount = produced.collect_fertilizer()
        assert amount == 1
        assert result.fertilizer_available is False


class TestAnimalCare:
    def test_care_increments_bonus(self) -> None:
        animal = Animal(animal_type="GOOSE")
        cared = animal.care()
        assert cared.cared_today is True
        assert cared.pending_care_bonus == 1

    def test_care_escaped_animal_raises(self) -> None:
        animal = Animal(animal_type="GOOSE")
        escaped = animal.skip_feed().skip_feed()
        with pytest.raises(ValueError, match="escaped"):
            escaped.care()
