from agent.domain import animal as animal_domain


def test_animal_defaults() -> None:
    a = animal_domain.Animal(animal_type="GOOSE")
    assert a.animal_type == "GOOSE"
    assert a.hunger == 0
    assert a.is_alive is True
