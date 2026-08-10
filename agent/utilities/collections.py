from collections import defaultdict


def default_dict_factory() -> defaultdict[int, int]:
    return defaultdict(int)
