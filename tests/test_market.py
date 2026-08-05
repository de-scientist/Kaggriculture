from agent.domain import market as market_domain


def test_market_state_defaults():
    m = market_domain.MarketState()
    assert m.inventory == {}
    assert m.prices == {}
