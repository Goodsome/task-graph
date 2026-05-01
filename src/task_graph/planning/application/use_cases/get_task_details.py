from dataclasses import dataclass
from pydantic import BaseModel, Field
from task_graph.planning.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.value_objects.task_id import TaskId


class GetTaskDetailsQuery(BaseModel):
    task_id: str = Field(..., description="The ID of the task to retrieve details for")


class GetTaskDetailsResult(BaseModel):
    """Result of getting task details."""

    success: bool
    task: Task | None = None
    error: str | None = None


@dataclass
class GetTaskDetails:
    """Use case to get details of a specific task."""

    uow: UnitOfWork

    def execute(self, query: GetTaskDetailsQuery) -> GetTaskDetailsResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(query.task_id)
                task = self.uow.tasks.get(task_id)
                return GetTaskDetailsResult(success=True, task=task)
        except Exception as e:
            return GetTaskDetailsResult(success=False, error=str(e))
