from task_graph.planning.domain.core.base_task import BaseTask


class TaskReadyEvent(BaseTask):
    """Event emitted when a task is ready to be claimed."""
    pass
