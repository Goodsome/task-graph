from task_graph.planning.domain.core.base_task_event import BaseTaskEvent


class TaskDelegated(BaseTaskEvent):
    """Event emitted when a task has been decomposed and sub-tasks are created."""
    pass
