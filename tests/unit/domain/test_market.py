"""Unit tests for the Market domain model (chapter 9)."""

from __future__ import annotations

import pytest

from agent.domain.market import Market
from agent.domain.prices import Price


class TestMarketConstruction:
    def test_defaults(self) -> None:
        market = Market()
        assert market.inventory == {}
        assert market.prices == {}

    def test_with_prices(self) -> None:
        market = Market(prices={"WHEAT": 25})
        assert market.prices == {"WHEAT": 25}

    def test_with_inventory(self) -> None:
        market = Market(inventory={"WHEAT": 100})
        assert market.inventory == {"WHEAT": 100}


class TestMarketPrices:
    def test_current_price_existing(self) -> None:
        market = Market(prices={"WHEAT": 25})
        price = market.current_price("WHEAT")
        assert price.value == 25

    def test_current_price_missing_defaults_to_one(self) -> None:
        market = Market()
        price = market.current_price("WHEAT")
        assert price.value == 1

    def test_update_price(self) -> None:
        market = Market(prices={"WHEAT": 25})
        updated = market.update_price("WHEAT", 30)
        assert updated.prices["WHEAT"] == 30

    def test_update_price_stores_history(self) -> None:
        market = Market(prices={"WHEAT": 25})
        updated = market.update_price("WHEAT", 30)
        assert len(updated.history) == 1
        assert updated.history[0]["WHEAT"] == 25

    def test_update_price_below_one_raises(self) -> None:
        market = Market(prices={"WHEAT": 25})
        with pytest.raises(ValueError, match="Price cannot be below 1"):
            market.update_price("WHEAT", 0)

    def test_update_price_does_not_mutate_original(self) -> None:
        market = Market(prices={"WHEAT": 25})
        market.update_price("WHEAT", 30)
        assert market.prices["WHEAT"] == 25


class TestMarketInventory:
    def test_update_inventory_increase(self) -> None:
        market = Market(inventory={"WHEAT": 100})
        updated = market.update_inventory("WHEAT", 50)
        assert updated.inventory["WHEAT"] == 150

    def test_update_inventory_add_new_item(self) -> None:
        market = Market()
        updated = market.update_inventory("WHEAT", 50)
        assert updated.inventory["WHEAT"] == 50

    def test_update_inventory_decrease(self) -> None:
        market = Market(inventory={"WHEAT": 100})
        updated = market.update_inventory("WHEAT", -30)
        assert updated.inventory["WHEAT"] == 70

    def test_update_inventory_clamps_negative_to_zero(self) -> None:
        market = Market(inventory={"WHEAT": 50})
        updated = market.update_inventory("WHEAT", -100)
        assert updated.inventory["WHEAT"] == 0


class TestMarketROI:
    def test_positive_roi(self) -> None:
        market = Market()
        assert market.estimate_roi("WHEAT", 10.0, 15.0) == 0.5

    def test_zero_cost_roi(self) -> None:
        market = Market()
        assert market.estimate_roi("WHEAT", 0.0, 15.0) == 0.0

    def test_negative_roi(self) -> None:
        market = Market()
        assert market.estimate_roi("WHEAT", 20.0, 10.0) == -0.5


class TestPriceComparison:
    def test_price_less_than(self) -> None:
        assert Price(value=10) < Price(value=20)

    def test_price_greater_than(self) -> None:
        assert Price(value=20) > Price(value=10)

    def test_price_equal(self) -> None:
        assert Price(value=15) == Price(value=15)

    def test_price_addition(self) -> None:
        p = Price(value=10) + 5
        assert p.value == 15

    def test_price_subtraction_floor(self) -> None:
        p = Price(value=5) - 10
        assert p.value == 0

    def test_price_multiplication(self) -> None:
        p = Price(value=10) * 1.5
        assert p.value == 15

    def test_pct_change(self) -> None:
        old = Price(value=10)
        new = Price(value=15)
        assert new.pct_change(old) == 50.0
