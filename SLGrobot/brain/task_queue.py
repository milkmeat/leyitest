"""Task Queue - Manage ordered task queue with priority."""

import json
import os
import logging
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """A single game task to execute."""
    name: str
    priority: int = 0  # Higher = more urgent
    params: dict = field(default_factory=dict)
    status: str = "pending"  # "pending" | "running" | "done" | "failed"
    retry_count: int = 0
    max_retries: int = 3


class TaskQueue:
    """Priority-ordered task queue.

    Tasks are sorted by priority (descending). Higher priority tasks
    are returned first by next().
    """

    def __init__(self) -> None:
        self._queue: list[Task] = []

    def add(self, task: Task) -> None:
        """Add task, maintaining priority order (highest first)."""
        self._queue.append(task)
        self._queue.sort(key=lambda t: t.priority, reverse=True)
        logger.info(f"Task added: '{task.name}' priority={task.priority}")

    def add_tasks(self, tasks: list[Task]) -> None:
        """Add multiple tasks (e.g. from LLM plan)."""
        for task in tasks:
            self._queue.append(task)
        self._queue.sort(key=lambda t: t.priority, reverse=True)
        logger.info(f"Added {len(tasks)} tasks to queue")

    def next(self) -> Task | None:
        """Return highest-priority pending task and mark it running.

        Returns None if no pending tasks.
        """
        for task in self._queue:
            if task.status == "pending":
                task.status = "running"
                logger.info(f"Task started: '{task.name}'")
                return task
        return None

    def has_pending(self) -> bool:
        """Check if there are pending tasks."""
        return any(t.status == "pending" for t in self._queue)

    def mark_done(self, task: Task) -> None:
        """Mark a task as completed."""
        task.status = "done"
        logger.info(f"Task done: '{task.name}'")

    def mark_failed(self, task: Task) -> None:
        """Mark a task as failed. Re-queue if retries remain."""
        task.retry_count += 1
        if task.retry_count < task.max_retries:
            task.status = "pending"
            logger.warning(
                f"Task failed, retrying ({task.retry_count}/{task.max_retries}): "
                f"'{task.name}'"
            )
        else:
            task.status = "failed"
            logger.error(f"Task failed permanently: '{task.name}'")

    def get_status(self) -> list[dict]:
        """Return summary of all tasks in the queue."""
        return [
            {
                "name": t.name,
                "priority": t.priority,
                "status": t.status,
                "retry_count": t.retry_count,
            }
            for t in self._queue
        ]

    def clear_completed(self) -> int:
        """Remove done/failed tasks from queue. Returns count removed."""
        before = len(self._queue)
        self._queue = [t for t in self._queue if t.status in ("pending", "running")]
        removed = before - len(self._queue)
        if removed:
            logger.debug(f"Cleared {removed} completed tasks")
        return removed

    def size(self) -> int:
        """Total number of tasks in queue (all statuses)."""
        return len(self._queue)

    def pending_count(self) -> int:
        """Number of pending tasks."""
        return sum(1 for t in self._queue if t.status == "pending")

    def save(self, filepath: str) -> None:
        """Save task queue to JSON file."""
        data = [asdict(t) for t in self._queue]
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(data)} tasks to {filepath}")

    def load(self, filepath: str) -> int:
        """Load task queue from JSON file. Returns number of tasks loaded."""
        if not os.path.exists(filepath):
            logger.warning(f"Task file not found: {filepath}")
            return 0

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._queue.clear()
        for item in data:
            self._queue.append(Task(**item))
        self._queue.sort(key=lambda t: t.priority, reverse=True)
        logger.info(f"Loaded {len(self._queue)} tasks from {filepath}")
        return len(self._queue)
