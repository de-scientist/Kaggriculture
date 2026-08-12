from agent.domain import worker as worker_domain
from agent.domain.position import Position


def test_worker_defaults() -> None:
    pos = Position(0, 0)
    w = worker_domain.Worker(worker_id="farmer", position=pos)
    assert w.position == pos
    assert w.available is True
    assert w.task is None
