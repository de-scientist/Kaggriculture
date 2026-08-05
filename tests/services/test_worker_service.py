from agent.domain.worker import Worker
from agent.domain.position import Position
from agent.services import worker_service


def test_assign_task():
    pos = Position(0, 0)
    worker = Worker(worker_id="farmer", position=pos)
    result = worker_service.assign(worker, task="plant")
    assert result.task == "plant"
    assert result.available is False


def test_release():
    pos = Position(0, 0)
    worker = Worker(worker_id="farmer", position=pos)
    assigned = worker_service.assign(worker, task="plant")
    result = worker_service.release(assigned)
    assert result.task is None
    assert result.available is True


def test_available_workers():
    pos = Position(0, 0)
    w1 = Worker(worker_id="farmer", position=pos)
    w2 = Worker(worker_id="hand1", position=pos)
    assigned = worker_service.assign(w2, task="plant")
    result = worker_service.available_workers([w1, assigned])
    assert len(result) == 1
    assert result[0].id == "farmer"


def test_busy_workers():
    pos = Position(0, 0)
    w1 = Worker(worker_id="farmer", position=pos)
    w2 = Worker(worker_id="hand1", position=pos)
    assigned = worker_service.assign(w2, task="plant")
    result = worker_service.busy_workers([w1, assigned])
    assert len(result) == 1
    assert result[0].id == "hand1"


def test_idle_workers():
    pos = Position(0, 0)
    w1 = Worker(worker_id="farmer", position=pos)
    w2 = Worker(worker_id="hand1", position=pos)
    assigned = worker_service.assign(w2, task="plant")
    result = worker_service.idle_workers([w1, assigned])
    assert len(result) == 1
    assert result[0].id == "farmer"


def test_current_tasks():
    pos = Position(0, 0)
    w1 = Worker(worker_id="farmer", position=pos)
    w2 = Worker(worker_id="hand1", position=pos)
    assigned = worker_service.assign(w2, task="plant")
    result = worker_service.current_tasks([w1, assigned])
    assert len(result) == 1
    assert result[0] == "plant"