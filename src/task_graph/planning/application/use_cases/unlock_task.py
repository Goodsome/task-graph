from dataclasses import dataclass
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.aggregates.task import IllegalStateTransitionError
from task_graph.planning.domain.services.dependency_resolution_service import (
    DependencyResolutionService,
)
from task_graph.planning.domain.value_objects.task_id import TaskId
from typing import Self
from task_graph.planning.application.dtos.unlock_task_command import UnlockTaskCommand
from task_graph.planning.application.dtos.unlock_task_result import UnlockTaskResult


@dataclass
class UnlockTask:
    uow: UnitOfWork[TaskRepository]
    resolution_service: DependencyResolutionService

    def execute(self: Self, cmd: UnlockTaskCommand) -> UnlockTaskResult:
        try:
            with self.uow:
                try:
                    task_id = TaskId.model_validate(cmd.task_id)
                except (ValueError, AttributeError):
                    return UnlockTaskResult(
                        success=False,
                        task_id=cmd.task_id,
                        error=f"Task {cmd.task_id} not found: invalid ID format",
                        error_code="TASK_NOT_FOUND",
                    )
                task = self.uow.repository.get(task_id)
                is_blocked = self.resolution_service.evaluate_blocking_status(
                    task, self.uow.repository
                )
                if is_blocked:
                    return UnlockTaskResult(
                        success=False,
                        task_id=cmd.task_id,
                        error="Task dependencies are not satisfied",
                        error_code="TASK_BLOCKED",
                    )
                task.mark_ready()
                self.uow.repository.save(task)
                self.uow.commit()
                return UnlockTaskResult(success=True, task_id=cmd.task_id)
        except IllegalStateTransitionError as e:
            return UnlockTaskResult(
                success=False,
                task_id=cmd.task_id,
                error=str(e),
                error_code="TASK_NOT_UNLOCKABLE",
            )
        except Exception as e:
            return UnlockTaskResult(
                success=False,
                task_id=cmd.task_id,
                error=f"Internal error: {str(e)}",
                error_code="INTERNAL_ERROR",
            )
