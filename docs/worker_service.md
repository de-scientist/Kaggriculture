# Worker Service

## Purpose

The worker service manages the main farmer and hired farm hands: their positions, inventories, and actions.

## Responsibilities

- Track farmer and hand positions on the grid
- Manage hand hiring and cost calculation (fibonacci sequence)
- Assign tasks to hands
- Coordinate movement for all workers
- Reset hand state at the start of each day

## Public Interfaces

### `WorkerService`

```python
class WorkerService:
    def hire_hand(self, player: Player) -> int: ...
    def assign_task(self, worker: Worker, task: Task) -> None: ...
    def move_worker(self, worker: Worker, direction: str) -> bool: ...
    def reset_daily_state(self) -> None: ...
```

### `WorkerManager`

Manages the lifecycle of all workers for a player.

### `TaskScheduler`

Prioritizes and schedules tasks for workers.

## Extension Points

- Add new worker types or roles.
- Implement smarter task assignment in `TaskScheduler`.
- Add hand skill levels or specializations.