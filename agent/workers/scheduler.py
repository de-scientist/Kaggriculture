def schedule_tasks(tasks: list, workers: list) -> list:
    assignments = []
    for i, task in enumerate(tasks):
        if i < len(workers):
            assignments.append((workers[i], task))
    return assignments