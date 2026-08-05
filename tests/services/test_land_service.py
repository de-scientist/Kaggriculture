from agent.services import land_service


def test_purchase_cost_ne():
    assert land_service.purchase_cost("NE") == 1000


def test_purchase_cost_sw():
    assert land_service.purchase_cost("SW") == 2000


def test_purchase_cost_se():
    assert land_service.purchase_cost("SE") == 4000


def test_purchase_cost_unknown():
    assert land_service.purchase_cost("NW") == 0


def test_neighboring_quadrants():
    result = land_service.neighboring_quadrants("NW")
    assert "NE" in result
    assert "SW" in result


def test_available_land():
    class FakeFarm:
        def __init__(self, quadrants):
            self.quadrants = quadrants

    farm = FakeFarm(["NW"])
    result = land_service.available_land(farm)
    assert "NE" in result
    assert "SW" in result
    assert "SE" in result
    assert "NW" not in result


def test_expandable():
    class FakeFarm:
        def __init__(self, quadrants):
            self.quadrants = quadrants

    farm = FakeFarm(["NW"])
    result = land_service.expandable(farm, money=5000)
    assert "NE" in result
    assert "SW" in result
    assert "SE" in result


def test_expandable_limited_funds():
    class FakeFarm:
        def __init__(self, quadrants):
            self.quadrants = quadrants

    farm = FakeFarm(["NW"])
    result = land_service.expandable(farm, money=500)
    assert "NE" not in result


def test_expected_land_value():
    assert land_service.expected_land_value("NE") == 1500.0
    assert land_service.expected_land_value("SW") == 3000.0
    assert land_service.expected_land_value("SE") == 6000.0


def test_expected_land_value_unknown():
    assert land_service.expected_land_value("NW") == 0.0
