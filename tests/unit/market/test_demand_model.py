"""Unit tests for Demand Model (Stage 2)."""
from __future__ import annotations

from agent.market.demand_model import DemandHistory, DemandModel, DemandSignal


class TestDemandHistory:
    def test_add_signal(self) -> None:
        history = DemandHistory(product="WHEAT")
        signal = DemandSignal(turn=0, product="WHEAT", inventory_change=-5,
                              price_change=2.0, sales_volume=3)
        history.add(signal)
        assert len(history.signals) == 1

    def test_recent_signals(self) -> None:
        history = DemandHistory(product="WHEAT")
        for i in range(15):
            history.add(DemandSignal(turn=i, product="WHEAT",
                                     inventory_change=-1, price_change=0.5,
                                     sales_volume=1))
        recent = history.recent_signals(10)
        assert len(recent) == 10
        assert recent[-1].turn == 14


class TestDemandModel:
    def test_record_single_observation(self) -> None:
        model = DemandModel()
        model.record(
            turn=1,
            prev_inventory={"WHEAT": 20},
            curr_inventory={"WHEAT": 15},
            prev_prices={"WHEAT": 10},
            curr_prices={"WHEAT": 12},
            sales={"WHEAT": 5},
        )
        history = model.get("WHEAT")
        assert history is not None
        assert len(history.signals) == 1

    def test_record_multiple_observations(self) -> None:
        model = DemandModel()
        model.record(1, {"WHEAT": 20}, {"WHEAT": 15}, {"WHEAT": 10}, {"WHEAT": 12}, {"WHEAT": 5})
        model.record(2, {"WHEAT": 15}, {"WHEAT": 10}, {"WHEAT": 12}, {"WHEAT": 14}, {"WHEAT": 5})
        model.record(3, {"WHEAT": 10}, {"WHEAT": 8}, {"WHEAT": 14}, {"WHEAT": 15}, {"WHEAT": 2})

        history = model.get("WHEAT")
        assert history is not None
        assert history.count() == 3
        assert history.demand_trend() < 0  # inventory decreasing

    def test_get_missing_product(self) -> None:
        model = DemandModel()
        assert model.get("MELON") is None

    def test_reset(self) -> None:
        model = DemandModel()
        model.record(1, {"WHEAT": 20}, {"WHEAT": 15}, {"WHEAT": 10}, {"WHEAT": 12}, {"WHEAT": 5})
        model.reset()
        assert model.get("WHEAT") is None

    def test_summary(self) -> None:
        model = DemandModel()
        model.record(1, {"WHEAT": 20}, {"WHEAT": 15}, {"WHEAT": 10}, {"WHEAT": 12}, {"WHEAT": 5})
        summary = model.summary()
        assert "trends" in summary
        assert "strengths" in summary
        assert "products_tracked" in summary
        assert "WHEAT" in summary["products_tracked"]
