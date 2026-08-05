from agent.domain import animal as animal_domain


def test_animal_defaults():
    a = animal_domain.Animal()
    assert a.kind == ""
    assert a.animal == ""
