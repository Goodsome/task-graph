from task_graph.planning.domain.enums import TaskStatus
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from dataclasses import dataclass
from task_graph.planning.domain.value_objects import TaskId
from task_graph.planning.application.dtos.update_task_status_command import (
    UpdateTaskStatusCommand,
)
from task_graph.planning.application.dtos.update_task_status_result import (
    UpdateTaskStatusResult,
)
from task_graph.planning.domain.services.dependency_resolution_service import (
    DependencyResolutionService,
)
from typing import Self

_STATUS_TO_METHOD: dict[TaskStatus, str] = {
    TaskStatus.READY: "mark_ready",
    TaskStatus.IN_PROGRESS: "claim",
    TaskStatus.DONE: "mark_completed",
}


@dataclass
class UpdateTaskStatus:
    """Updates a task's status and triggers chain reactions for dependents."""

    uow: UnitOfWork[TaskRepository]
    resolution_service: DependencyResolutionService

    def execute(self: Self, cmd: UpdateTaskStatusCommand) -> UpdateTaskStatusResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.repository.get(task_id)
                try:
                    new_status_enum = TaskStatus(cmd.new_status.lower())
                except ValueError:
                    return UpdateTaskStatusResult(
                        success=False, error= f"Invalid status: {cmd.new_status}"
                    )
                method_name = _STATUS_TO_METHOD.get(new_status_enum)
                if method_name is None:
                    return UpdateTaskStatusResult(
                       success= False,
                       error= f"Status '{cmd.new_status}' cannot be set directly via this use case",
                    )
                getattr(task, method_name)()
                self.uow.repository.save(task)
                self.uow.commit()
                return UpdateTaskStatusResult(success= True)
        except Exception as e:
            return UpdateTaskStatusResult(success= False, error= str(e))
