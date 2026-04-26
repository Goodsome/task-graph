from task_graph.planning.domain.core.base_task import BaseTask


class TaskInProgressEvent(BaseTask):
    """Event emitted when a task is claimed and starts execution."""
    pass
