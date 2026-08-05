from agent.domain import worker as worker_domain


def hire_hand() -> dict:
    return {"kind": "HIRE"}


def assign_task(worker: dict, task: dict) -> dict:
    return {"worker": worker, "task": task}


def move_worker(worker: dict, direction: str) -> dict:
    return {"worker": worker, "direction": direction}