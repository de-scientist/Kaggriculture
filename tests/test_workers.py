from agent.domain import worker as worker_domain


def test_worker_defaults():
    w = worker_domain.Worker()
    assert w.position == []
    assert w.inventory == {}
    assert w.busy is False
