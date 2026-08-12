"""Unit tests for Price Tracker (Stage 2)."""

from __future__ import annotations

from agent.market.price_tracker import PriceHistory, PriceSnapshot, PriceTracker


class TestPriceTracker:
    def test_record_single_turn(self) -> None:
        tracker = PriceTracker()
        tracker.record(turn=0, prices={"WHEAT": 10}, inventory={"WHEAT": 20})
        assert "WHEAT" in tracker.products_tracked()
        assert tracker.products_tracked() == ["WHEAT"]

    def test_record_multiple_turns(self) -> None:
        tracker = PriceTracker()
        tracker.record(turn=0, prices={"WHEAT": 10}, inventory={"WHEAT": 20})
        tracker.record(turn=1, prices={"WHEAT": 12}, inventory={"WHEAT": 18})
        tracker.record(turn=2, prices={"WHEAT": 15}, inventory={"WHEAT": 15})

        history = tracker.get_history("WHEAT")
        assert history is not None
        assert history.count() == 3
        assert history.current_price() == 15.0

    def test_current_prices(self) -> None:
        tracker = PriceTracker()
        tracker.record(0, {"WHEAT": 10, "CARROT": 20}, {"WHEAT": 5, "CARROT": 3})
        prices = tracker.current_prices()
        assert prices["WHEAT"] == 10.0
        assert prices["CARROT"] == 20.0

    def test_get_history_missing_product(self) -> None:
        tracker = PriceTracker()
        assert tracker.get_history("MELON") is None

    def test_reset(self) -> None:
        tracker = PriceTracker()
        tracker.record(0, {"WHEAT": 10}, {"WHEAT": 5})
        assert len(tracker.products_tracked()) > 0
        tracker.reset()
        assert len(tracker.products_tracked()) == 0


class TestPriceHistory:
    def test_current_price_empty(self) -> None:
        history = PriceHistory(product="WHEAT")
        assert history.current_price() is None

    def test_current_price_after_add(self) -> None:
        history = PriceHistory(product="WHEAT")
        history.add(PriceSnapshot(turn=0, product="WHEAT", price=10.0, inventory=20))
        assert history.current_price() == 10.0

    def test_prices_list(self) -> None:
        history = PriceHistory(product="WHEAT")
        history.add(PriceSnapshot(turn=0, product="WHEAT", price=10.0, inventory=20))
        history.add(PriceSnapshot(turn=1, product="WHEAT", price=12.0, inventory=18))
        assert history.prices_list() == [10.0, 12.0]
