from dataclasses import dataclass
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.domain.exceptions import TaskNotClaimableError
from task_graph.planning.domain.services.dependency_resolution_service import (
    DependencyResolutionService,
)
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.application.dtos.claim_task_command import ClaimTaskCommand
from typing import Self
from task_graph.planning.application.dtos.claim_task_result import ClaimTaskResult


@dataclass
class ClaimTask:
    uow: UnitOfWork[TaskRepository]
    dependency_service: DependencyResolutionService

    def execute(self: Self, cmd: ClaimTaskCommand) -> ClaimTaskResult:
        try:
            with self.uow:
                try:
                    task_id = TaskId.model_validate(cmd.task_id)
                except (ValueError, AttributeError):
                    return ClaimTaskResult(
                        success=False,
                        task_id=cmd.task_id,
                        error=f"Task {cmd.task_id} not found: invalid ID format",
                        error_code="TASK_NOT_FOUND",
                    )
                task = self.uow.repository.get(task_id)
                if not task.is_claimable():
                    error_code = (
                        "ALREADY_CLAIMED"
                        if task.status == TaskStatus.IN_PROGRESS
                        else "TASK_NOT_READY"
                    )
                    return ClaimTaskResult(
                        success=False,
                        task_id=cmd.task_id,
                        error=f"Task is not ready: current status is {task.status}",
                        error_code=error_code,
                    )
                task.claim()
                self.uow.repository.save(task)
                self.uow.commit()
                return ClaimTaskResult(success=True, task_id=cmd.task_id)
        except TaskNotClaimableError as e:
            return ClaimTaskResult(
                success=False,
                task_id=cmd.task_id,
                error=str(e),
                error_code="TASK_NOT_READY",
            )
        except Exception as e:
            return ClaimTaskResult(
                success=False,
                task_id=cmd.task_id,
                error=f"Internal error: {str(e)}",
                error_code="INTERNAL_ERROR",
            )
