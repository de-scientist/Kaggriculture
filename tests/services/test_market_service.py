from agent.domain.market import Market
from agent.services import market_service


def test_buy_price():
    m = Market(prices={"WHEAT": 15})
    result = market_service.buy_price(m, "WHEAT")
    assert result.value == 15


def test_sell_price():
    m = Market(prices={"WHEAT": 15})
    result = market_service.sell_price(m, "WHEAT")
    assert result.value == 15


def test_current_prices():
    m = Market(prices={"WHEAT": 15, "CARROT": 8})
    result = market_service.current_prices(m)
    assert result["WHEAT"] == 15
    assert result["CARROT"] == 8


def test_price_history():
    m = Market(prices={"WHEAT": 15})
    m = m.update_price("WHEAT", 18)
    history = market_service.price_history(m)
    assert len(history) == 1
    assert history[0]["WHEAT"] == 15


def test_best_sell_option():
    m = Market(prices={"WHEAT": 15, "CARROT": 8})
    result = market_service.best_sell_option(m, ["WHEAT", "CARROT"])
    assert result is not None
    assert result[0] == "WHEAT"
    assert result[1].value == 15


def test_best_sell_option_empty():
    m = Market(prices={})
    result = market_service.best_sell_option(m, [])
    assert result is None


def test_best_buy_option():
    m = Market(prices={"WHEAT": 15, "CARROT": 8})
    result = market_service.best_buy_option(m, ["WHEAT", "CARROT"])
    assert result is not None
    assert result[0] == "CARROT"
    assert result[1].value == 8


def test_best_buy_option_empty():
    m = Market(prices={})
    result = market_service.best_buy_option(m, [])
    assert result is None


def test_market_snapshot():
    m = Market(prices={"WHEAT": 15}, inventory={"WHEAT": 100})
    snapshot = market_service.MarketSnapshot.from_market(m, turn=5)
    assert snapshot.prices == {"WHEAT": 15}
    assert snapshot.inventory == {"WHEAT": 100}
    assert snapshot.turn == 5
