from agent.planning import priority_queue, scheduler, task_planner


def plan(context: dict) -> list:
    tasks = task_planner.generate_tasks(context)
    ordered = priority_queue.order(tasks)
    return scheduler.schedule(ordered)
