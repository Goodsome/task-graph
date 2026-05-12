from pydantic import BaseModel, Field
from task_graph.planning.domain.value_objects.sub_task_info import SubTaskInfo


class SubmitTaskResultCommand(BaseModel):
    """Command to submit task execution result."""

    task_id: str
    summary: str
    artifacts: list[str] = Field(default_factory=list)
    error: str | None = Field(default=None)
    sub_tasks: list[SubTaskInfo] = Field(default_factory=list)
