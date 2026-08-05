import time


def now_ms() -> int:
    return int(time.time() * 1000)


def elapsed(start_ms: int) -> int:
    return now_ms() - start_ms
