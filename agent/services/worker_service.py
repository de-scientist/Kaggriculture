from agent.domain.worker import Worker
from agent.domain.position import Position


def assign_task(worker: Worker, task: object) -> Worker:
    return worker.assign_task(task)


def move_worker(worker: Worker, new_position: Position) -> Worker:
    return worker.move(new_position)


def finish_task(worker: Worker) -> Worker:
    return worker.finish_task()


def reset_daily(worker: Worker) -> Worker:
    return worker.reset_daily()