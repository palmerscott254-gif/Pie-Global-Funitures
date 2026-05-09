"""Background task abstraction for async operations.

This module provides a pluggable interface for async tasks.
Currently uses threading; can be replaced with Celery without changing views.
"""
import logging
import threading
from abc import ABC, abstractmethod
from typing import Callable, Any, Dict, Optional

logger = logging.getLogger(__name__)


class TaskRunner(ABC):
    """Abstract base for task execution backends."""

    @abstractmethod
    def enqueue(self, func: Callable, *args, **kwargs) -> str:
        """Enqueue a task for execution."""
        pass


class ThreadingTaskRunner(TaskRunner):
    """Execute tasks using native threading (default, no external deps)."""

    def enqueue(self, func: Callable, *args, **kwargs) -> str:
        """Run task in daemon thread."""
        task_id = str(id(func))
        try:
            thread = threading.Thread(
                target=self._safe_execute,
                args=(func, args, kwargs),
                daemon=True,
                name=f"task-{task_id}",
            )
            thread.start()
            logger.debug(f"Task enqueued: {func.__name__} (thread: {task_id})")
            return task_id
        except Exception as e:
            logger.exception(f"Failed to enqueue task: {func.__name__}")
            raise

    @staticmethod
    def _safe_execute(func: Callable, args: tuple, kwargs: dict) -> None:
        """Execute function with exception handling."""
        try:
            func(*args, **kwargs)
        except Exception:
            logger.exception(f"Task failed: {func.__name__}")


class CeleryTaskRunner(TaskRunner):
    """Execute tasks using Celery (optional production backend)."""

    def __init__(self, celery_app=None):
        """Initialize with Celery app instance."""
        self.celery_app = celery_app

    def enqueue(self, func: Callable, *args, **kwargs) -> str:
        """Enqueue task via Celery."""
        if not self.celery_app:
            raise RuntimeError("Celery app not configured")
        # Delegate to Celery
        task = self.celery_app.send_task(
            func.__module__ + "." + func.__name__,
            args=args,
            kwargs=kwargs,
        )
        logger.debug(f"Task enqueued via Celery: {func.__name__} (id: {task.id})")
        return str(task.id)


# Global task runner instance (can be swapped at runtime)
_task_runner: Optional[TaskRunner] = None


def get_task_runner() -> TaskRunner:
    """Get the global task runner instance."""
    global _task_runner
    if _task_runner is None:
        # Default to threading; can be overridden via set_task_runner()
        _task_runner = ThreadingTaskRunner()
    return _task_runner


def set_task_runner(runner: TaskRunner) -> None:
    """Set the global task runner instance."""
    global _task_runner
    _task_runner = runner
    logger.info(f"Task runner set to: {runner.__class__.__name__}")


def enqueue_task(func: Callable, *args, **kwargs) -> str:
    """Enqueue a background task using the configured runner.
    
    Example:
        def send_email(email, subject, body):
            # Do work
            pass
        
        enqueue_task(send_email, "user@example.com", "Welcome", "Hello!")
    """
    runner = get_task_runner()
    return runner.enqueue(func, *args, **kwargs)


class BackgroundTaskMixin:
    """Mixin for views/services that execute background tasks."""

    def enqueue_task(self, func: Callable, *args, **kwargs) -> str:
        """Enqueue a background task."""
        return enqueue_task(func, *args, **kwargs)
