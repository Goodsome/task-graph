from task_graph.planning.domain.aggregates.task import Task
from pydantic import BaseModel, Field


class GetTaskDetailsResult(BaseModel):
    """Result of getting task details."""

    success: bool
    task: Task | None = Field(default=None)
    error: str | None = Field(default=None)
