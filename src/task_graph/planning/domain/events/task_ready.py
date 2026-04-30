from task_graph.planning.domain.core.base_task_event import BaseTaskEvent


class TaskReady(BaseTaskEvent):
    """Event emitted when a task is ready to be claimed."""
    pass
