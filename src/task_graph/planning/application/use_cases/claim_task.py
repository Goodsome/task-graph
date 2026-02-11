from dataclasses import dataclass, field
from task_graph.planning.domain.services.dependency_resolution_service import (
    DependencyResolutionService,
)
from task_graph.planning.domain.ports.task_repository import TaskRepository


@dataclass(frozen=True)
class ClaimTaskCommand:

    task_id: str
    executor_id: str = field(default_factory=str)


@dataclass(frozen=True)
class ClaimTaskResult:

    success: bool
    task_id: str
    error: str = field(default_factory=str)
    error_code: str = field(default_factory=str)


from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.domain.exceptions import TaskNotClaimableError

@dataclass
class ClaimTask:

    repository: TaskRepository
    dependency_service: DependencyResolutionService

    def execute(self, cmd: ClaimTaskCommand) -> ClaimTaskResult:
        try:
            # 1. Retrieve task
            try:
                task_id = TaskId.reconstitute(cmd.task_id)
            except (ValueError, AttributeError):
                return ClaimTaskResult(
                    success=False,
                    task_id=cmd.task_id,
                    error=f"Task {cmd.task_id} not found: invalid ID format",
                    error_code="TASK_NOT_FOUND"
                )
            
            task = self.repository.get(task_id)
            
            if not task:
                return ClaimTaskResult(
                    success=False,
                    task_id=cmd.task_id,
                    error=f"Task {cmd.task_id} not found",
                    error_code="TASK_NOT_FOUND"
                )
            
            # 2. Validate state
            if task.status != TaskStatus.READY:
                error_code = "ALREADY_CLAIMED" if task.status == TaskStatus.IN_PROGRESS else "TASK_NOT_READY"
                return ClaimTaskResult(
                    success=False,
                    task_id=cmd.task_id,
                    error=f"Task is not ready: current status is {task.status}",
                    error_code=error_code
                )
            
            # 3. Check dependencies (double-check even though READY implies unblocked)
            is_blocked = self.dependency_service.evaluate_blocking_status(task, self.repository)
            if is_blocked:
                return ClaimTaskResult(
                    success=False,
                    task_id=cmd.task_id,
                    error="Task dependencies are not satisfied",
                    error_code="TASK_BLOCKED"
                )
            
            # 4. Claim the task (domain method)
            task.claim()
            
            # 5. Persist
            self.repository.save(task)
            
            return ClaimTaskResult(
                success=True,
                task_id=cmd.task_id
            )
            
        except TaskNotClaimableError as e:
            return ClaimTaskResult(
                success=False,
                task_id=cmd.task_id,
                error=str(e),
                error_code="TASK_NOT_READY"
            )
        except Exception as e:
            return ClaimTaskResult(
                success=False,
                task_id=cmd.task_id,
                error=f"Internal error: {str(e)}",
                error_code="INTERNAL_ERROR"
            )
