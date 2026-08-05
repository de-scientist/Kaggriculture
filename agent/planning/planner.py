from agent.planning import task_planner
from agent.planning import priority_queue
from agent.planning import scheduler


def plan(context: dict) -> list:
    tasks = task_planner.generate_tasks(context)
    ordered = priority_queue.order(tasks)
    return scheduler.schedule(ordered)