from agent.domain import market as market_domain


def test_market_defaults() -> None:
    m = market_domain.Market()
    assert m.inventory == {}
    assert m.prices == {}
