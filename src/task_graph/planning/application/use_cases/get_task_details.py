from dataclasses import dataclass
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from task_graph.planning.application.unit_of_work import UnitOfWork
from task_graph.planning.domain.value_objects.task_id import TaskId

class GetTaskDetailsQuery(BaseModel):
    task_id: str = Field(..., description="The ID of the task to retrieve details for")

class GetTaskDetailsResult(BaseModel):
    """Result of getting task details."""
    success: bool
    task: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class GetTaskDetails:
    """Use case to get details of a specific task."""
    uow: UnitOfWork

    def execute(self, query: GetTaskDetailsQuery) -> GetTaskDetailsResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(query.task_id)
                task = self.uow.tasks.find_by_id(task_id)
                
                if task:
                    return GetTaskDetailsResult(
                        success=True,
                        task=task.to_dict()
                    )
                else:
                    return GetTaskDetailsResult(
                        success=False,
                        error=f"Task with ID {query.task_id} not found."
                    )
        except Exception as e:
            return GetTaskDetailsResult(
                success=False,
                error=str(e)
            )
