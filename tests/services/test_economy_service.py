from agent.services import economy_service


def test_roi() -> None:
    assert economy_service.roi(10.0, 15.0) == 0.5


def test_roi_zero_cost() -> None:
    assert economy_service.roi(0.0, 15.0) == 0.0


def test_profit() -> None:
    assert economy_service.profit(15.0, 10.0) == 5.0


def test_cost() -> None:
    assert economy_service.cost("WHEAT", 5, 2.0) == 10.0


def test_expected_return() -> None:
    assert economy_service.expected_return("WHEAT", 5, 3.0) == 15.0


def test_payback_period() -> None:
    assert economy_service.payback_period(100.0, 25.0) == 4


def test_payback_period_zero_return() -> None:
    assert economy_service.payback_period(100.0, 0.0) == -1
