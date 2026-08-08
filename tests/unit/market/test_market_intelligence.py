"""Unit tests for Market Intelligence Engine (Stage 2)."""
from __future__ import annotations

from agent.market.market_intelligence import MarketIntelligence, MarketIntelligenceEngine


class TestMarketIntelligence:
    def test_is_sell_opportunity_with_forecast(self) -> None:
        intel = MarketIntelligence(
            product="WHEAT",
            current_price=45.0,
            forecast=None,
            demand_trend=0.0,
            demand_strength=0.5,
            inventory=10,
        )
        # No forecast → sell when uncertain
        assert intel.is_sell_opportunity is True

    def test_is_buy_opportunity_no_forecast(self) -> None:
        intel = MarketIntelligence(
            product="WHEAT",
            current_price=5.0,
            forecast=None,
            demand_trend=0.0,
            demand_strength=0.5,
            inventory=10,
        )
        assert intel.is_buy_opportunity is False

    def test_confidence_without_forecast(self) -> None:
        intel = MarketIntelligence(
            product="WHEAT",
            current_price=10.0,
            forecast=None,
            demand_trend=0.0,
            demand_strength=0.5,
            inventory=10,
        )
        assert intel.confidence == 0.3


class TestMarketIntelligenceEngine:
    def test_update_and_retrieve(self) -> None:
        engine = MarketIntelligenceEngine()
        engine.update(turn=0, prices={"WHEAT": 10}, inventory={"WHEAT": 20})
        engine.update(turn=1, prices={"WHEAT": 12}, inventory={"WHEAT": 18})

        intel = engine.get_intelligence("WHEAT", 12, 18)
        assert intel.product == "WHEAT"
        assert intel.current_price == 12.0
        assert intel.inventory == 18

    def test_sell_recommendation(self) -> None:
        engine = MarketIntelligenceEngine()
        result = engine.sell_recommendation("WHEAT", 10, 5)
        assert isinstance(result, bool)

    def test_buy_recommendation(self) -> None:
        engine = MarketIntelligenceEngine()
        result = engine.buy_recommendation("WHEAT", 5, 10)
        assert isinstance(result, bool)

    def test_reset(self) -> None:
        engine = MarketIntelligenceEngine()
        engine.update(0, {"WHEAT": 10}, {"WHEAT": 20})
        assert engine.products_tracked() != []
        engine.reset()
        assert engine.products_tracked() == []

    def test_get_all_intelligence(self) -> None:
        engine = MarketIntelligenceEngine()
        engine.update(0, {"WHEAT": 10, "CARROT": 20}, {"WHEAT": 5, "CARROT": 3})
        intel = engine.get_all_intelligence({"WHEAT": 10, "CARROT": 20}, {"WHEAT": 5, "CARROT": 3})
        assert "WHEAT" in intel
        assert "CARROT" in intel
