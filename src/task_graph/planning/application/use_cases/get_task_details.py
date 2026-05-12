from dataclasses import dataclass
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.application.dtos.get_task_details_result import (
    GetTaskDetailsResult,
)
from task_graph.planning.application.dtos.get_task_details_query import (
    GetTaskDetailsQuery,
)
from typing import Self


@dataclass
class GetTaskDetails:
    """Use case to get details of a specific task."""

    uow: UnitOfWork[TaskRepository]

    def execute(self: Self, query: GetTaskDetailsQuery) -> GetTaskDetailsResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(query.task_id)
                task = self.uow.repository.get(task_id)
                return GetTaskDetailsResult(success=True, task=task)
        except Exception as e:
            return GetTaskDetailsResult(success=False, error=str(e))
