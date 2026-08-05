from agent.domain.animal import Animal


def feed(animal: Animal) -> Animal:
    return animal.feed()


def skip_feed(animal: Animal) -> Animal:
    return animal.skip_feed()


def care(animal: Animal) -> Animal:
    return animal.care()


def produce(animal: Animal) -> tuple[Animal, int]:
    return animal.produce()


def collect_fertilizer(animal: Animal) -> tuple[Animal, int]:
    return animal.collect_fertilizer()