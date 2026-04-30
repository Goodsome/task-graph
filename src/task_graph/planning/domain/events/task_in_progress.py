from task_graph.planning.domain.core.base_task_event import BaseTaskEvent


class TaskInProgress(BaseTaskEvent):
    """Event emitted when a task is claimed and starts execution."""
    pass
