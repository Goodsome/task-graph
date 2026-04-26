from pydantic import Field
from task_graph.planning.domain.core.base_task import BaseTask


class TaskBlockedEvent(BaseTask):
    """Event emitted when a task is blocked (e.g., execution error)."""
    reason: str = Field(description="Reason for being blocked")
