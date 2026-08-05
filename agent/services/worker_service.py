from __future__ import annotations

from agent.domain.worker import Worker


def assign(worker: Worker, task: object) -> Worker:
    return worker.assign_task(task)


def release(worker: Worker) -> Worker:
    return worker.finish_task()


def available_workers(workers: list[Worker]) -> list[Worker]:
    return [w for w in workers if w.available]


def busy_workers(workers: list[Worker]) -> list[Worker]:
    return [w for w in workers if not w.available]


def idle_workers(workers: list[Worker]) -> list[Worker]:
    return [w for w in workers if w.available and w.task is None]


def current_tasks(workers: list[Worker]) -> list[object]:
    return [w.task for w in workers if w.task is not None]