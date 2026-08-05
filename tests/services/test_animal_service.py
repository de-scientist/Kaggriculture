from agent.domain.animal import Animal
from agent.services import animal_service


def test_feed_animal():
    animal = Animal(animal_type="GOOSE")
    result = animal_service.feed(animal)
    assert result.fed_today is True


def test_feed_unfed_animal():
    animal = Animal(animal_type="GOOSE")
    assert animal_service.can_feed(animal) is True


def test_feed_already_fed_animal():
    animal = Animal(animal_type="GOOSE")
    fed = animal_service.feed(animal)
    assert animal_service.can_feed(fed) is False


def test_collect_from_fed_animal():
    animal = Animal(animal_type="GOOSE")
    fed = animal_service.feed(animal)
    result_animal, bonus = animal_service.collect(fed)
    assert isinstance(result_animal, Animal)


def test_collect_from_unfed_animal_raises():
    animal = Animal(animal_type="GOOSE")
    try:
        animal_service.collect(animal)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_can_feed():
    animal = Animal(animal_type="GOOSE")
    assert animal_service.can_feed(animal) is True


def test_can_feed_after_feeding():
    animal = Animal(animal_type="GOOSE")
    fed = animal_service.feed(animal)
    assert animal_service.can_feed(fed) is False


def test_can_collect():
    animal = Animal(animal_type="GOOSE")
    assert animal_service.can_collect(animal) is False


def test_can_collect_after_feeding():
    animal = Animal(animal_type="GOOSE")
    fed = animal_service.feed(animal)
    assert animal_service.can_collect(fed) is True


def test_expected_output():
    animal = Animal(animal_type="GOOSE")
    result = animal_service.expected_output(animal)
    assert result["animal_type"] == "GOOSE"
    assert result["fed_today"] is False
    assert result["is_alive"] is True


def test_production_status():
    animal = Animal(animal_type="GOOSE")
    result = animal_service.production_status(animal)
    assert result["animal_type"] == "GOOSE"
    assert result["hunger"] == 0
    assert result["health"] == 100
    assert result["is_alive"] is True