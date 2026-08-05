from agent.services import planning_service


def test_daily_plan():
    tasks = [{"name": "plant", "priority": 5}, {"name": "water", "priority": 3}]
    result = planning_service.daily_plan(None, tasks)
    assert result[0]["name"] == "plant"


def test_task_queue():
    tasks = [{"name": "plant"}, {"name": "water"}]
    result = planning_service.task_queue(tasks)
    assert len(result) == 2


def test_next_task():
    tasks = [{"name": "plant"}, {"name": "water"}]
    result = planning_service.next_task(tasks)
    assert result["name"] == "plant"


def test_next_task_empty():
    result = planning_service.next_task([])
    assert result is None


def test_prioritize():
    tasks = [{"name": "plant", "priority": 5}, {"name": "water", "priority": 3}]
    result = planning_service.prioritize(tasks, "priority")
    assert result[0]["name"] == "plant"
