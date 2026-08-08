"""Unit tests for the Inventory domain model (chapter 9)."""
from __future__ import annotations

import pytest

from agent.domain.inventory import Inventory


class TestInventoryConstruction:
    def test_defaults(self) -> None:
        inv = Inventory()
        assert inv.capacity == 100
        assert inv.items == {}

    def test_custom_capacity(self) -> None:
        inv = Inventory(capacity=50)
        assert inv.capacity == 50


class TestInventoryAdd:
    def test_add_new_item(self) -> None:
        inv = Inventory()
        result = inv.add("WHEAT", 5)
        assert result.count("WHEAT") == 5

    def test_add_existing_item(self) -> None:
        inv = Inventory().add("WHEAT", 3)
        result = inv.add("WHEAT", 2)
        assert result.count("WHEAT") == 5

    def test_add_zero_quantity_raises(self) -> None:
        inv = Inventory()
        with pytest.raises(ValueError, match="positive"):
            inv.add("WHEAT", 0)

    def test_add_negative_quantity_raises(self) -> None:
        inv = Inventory()
        with pytest.raises(ValueError, match="positive"):
            inv.add("WHEAT", -1)

    def test_add_exceeding_capacity_raises(self) -> None:
        inv = Inventory(capacity=10)
        with pytest.raises(ValueError, match="Inventory full"):
            inv.add("WHEAT", 15)

    def test_add_multiple_items(self) -> None:
        inv = Inventory()
        inv = inv.add("WHEAT", 3)
        inv = inv.add("CARROT", 2)
        assert inv.count("WHEAT") == 3
        assert inv.count("CARROT") == 2
        assert inv._total_count() == 5


class TestInventoryRemove:
    def test_remove_existing(self) -> None:
        inv = Inventory().add("WHEAT", 5)
        result = inv.remove("WHEAT", 3)
        assert result.count("WHEAT") == 2

    def test_remove_all(self) -> None:
        inv = Inventory().add("WHEAT", 5)
        result = inv.remove("WHEAT", 5)
        assert result.count("WHEAT") == 0
        assert "WHEAT" not in result.items

    def test_remove_nonexistent_raises(self) -> None:
        inv = Inventory()
        with pytest.raises(ValueError, match="Insufficient"):
            inv.remove("WHEAT", 1)

    def test_remove_insufficient_raises(self) -> None:
        inv = Inventory().add("WHEAT", 2)
        with pytest.raises(ValueError, match="Insufficient"):
            inv.remove("WHEAT", 5)

    def test_remove_zero_raises(self) -> None:
        inv = Inventory().add("WHEAT", 5)
        with pytest.raises(ValueError, match="positive"):
            inv.remove("WHEAT", 0)

    def test_remove_preserves_other_items(self) -> None:
        inv = Inventory().add("WHEAT", 5).add("CARROT", 3)
        result = inv.remove("WHEAT", 2)
        assert result.count("WHEAT") == 3
        assert result.count("CARROT") == 3


class TestInventoryQueries:
    def test_has_item_sufficient(self) -> None:
        inv = Inventory().add("WHEAT", 5)
        assert inv.has("WHEAT", 3) is True
        assert inv.has("WHEAT", 5) is True

    def test_has_item_insufficient(self) -> None:
        inv = Inventory().add("WHEAT", 2)
        assert inv.has("WHEAT", 3) is False

    def test_has_item_missing(self) -> None:
        inv = Inventory()
        assert inv.has("WHEAT", 1) is False

    def test_has_default_quantity(self) -> None:
        inv = Inventory().add("WHEAT", 1)
        assert inv.has("WHEAT") is True

    def test_count_missing_returns_zero(self) -> None:
        inv = Inventory()
        assert inv.count("WHEAT") == 0

    def test_space_remaining(self) -> None:
        inv = Inventory(capacity=10).add("WHEAT", 3)
        assert inv.space_remaining() == 7


class TestInventoryReserve:
    def test_reserve_removes_from_inventory(self) -> None:
        inv = Inventory().add("WHEAT", 5)
        reserved = inv.reserve("WHEAT", 2)
        assert reserved.count("WHEAT") == 3

    def test_reserve_insufficient_raises(self) -> None:
        inv = Inventory().add("WHEAT", 1)
        with pytest.raises(ValueError, match="Insufficient"):
            inv.reserve("WHEAT", 2)


class TestInventoryImmutability:
    def test_add_does_not_mutate_original(self) -> None:
        inv = Inventory().add("WHEAT", 5)
        inv.add("WHEAT", 3)
        assert inv.count("WHEAT") == 5

    def test_remove_does_not_mutate_original(self) -> None:
        inv = Inventory().add("WHEAT", 5)
        inv.remove("WHEAT", 3)
        assert inv.count("WHEAT") == 5

    def test_items_returns_copy(self) -> None:
        inv = Inventory().add("WHEAT", 5)
        items = inv.items
        items["WHEAT"] = 99
        assert inv.count("WHEAT") == 5
