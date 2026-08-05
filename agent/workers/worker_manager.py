from agent.domain import worker as worker_domain


def create_worker(position: list) -> dict:
    return {"position": position, "inventory": {}, "busy": False}


def count_hires(hires_today: int) -> int:
    return hires_today