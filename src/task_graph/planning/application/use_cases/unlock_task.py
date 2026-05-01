from dataclasses import dataclass, field

from task_graph.planning.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.aggregates.task import IllegalStateTransitionError
from task_graph.planning.domain.services.dependency_resolution_service import (
    DependencyResolutionService,
)
from task_graph.planning.domain.value_objects.task_id import TaskId


@dataclass(frozen=True)
class UnlockTaskCommand:
    task_id: str


@dataclass(frozen=True)
class UnlockTaskResult:
    success: bool
    task_id: str
    error: str = field(default_factory=str)
    error_code: str = field(default_factory=str)


@dataclass
class UnlockTask:
    uow: UnitOfWork
    resolution_service: DependencyResolutionService

    def execute(self, cmd: UnlockTaskCommand) -> UnlockTaskResult:
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

                task = self.uow.tasks.get(task_id)

                is_blocked = self.resolution_service.evaluate_blocking_status(
                    task, self.uow.tasks
                )
                if is_blocked:
                    return UnlockTaskResult(
                        success=False,
                        task_id=cmd.task_id,
                        error="Task dependencies are not satisfied",
                        error_code="TASK_BLOCKED",
                    )

                task.mark_ready()
                self.uow.tasks.save(task)
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
