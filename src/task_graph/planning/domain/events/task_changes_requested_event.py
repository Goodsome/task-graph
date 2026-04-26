from pydantic import Field
from task_graph.planning.domain.core.base_task import BaseTask


class TaskChangesRequestedEvent(BaseTask):
    """Event emitted when a task review is rejected and changes are requested."""
    feedback: str = Field(description="Review feedback describing required changes")
