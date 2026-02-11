from dataclasses import dataclass, field
from task_graph.planning.domain.services.dependency_resolution_service import (
    DependencyResolutionService,
)
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.enums import TaskStatus


@dataclass(frozen=True)
class ReviewTaskCommand:

    task_id: str
    approved: bool
    feedback: str


@dataclass(frozen=True)
class ReviewTaskResult:

    success: bool
    task_id: str
    affected_tasks: list[str] = field(default_factory=list)
    error: str = ""


@dataclass
class ReviewTask:

    repository: TaskRepository
    resolution_service: DependencyResolutionService

    def execute(self, cmd: ReviewTaskCommand) -> ReviewTaskResult:
        try:
            task_id = TaskId.reconstitute(cmd.task_id)
            task = self.repository.get(task_id)

            if not task:
                return ReviewTaskResult(
                    success=False,
                    task_id=cmd.task_id,
                    affected_tasks=[],
                    error=f"Task {cmd.task_id} not found"
                )

            task.review(approved=cmd.approved, feedback=cmd.feedback)
            self.repository.save(task)

            affected_tasks = []
            if task.is_done():
                dependents = self.repository.find_dependents(task.id)
                for dependent in dependents:
                    if dependent.status in [TaskStatus.BLOCKED, TaskStatus.PENDING]:
                        is_blocked = self.resolution_service.evaluate_blocking_status(dependent, self.repository)
                        
                        if not is_blocked:
                            dependent.status = TaskStatus.READY
                            self.repository.save(dependent)
                            affected_tasks.append(str(dependent.id.value))

            return ReviewTaskResult(
                success=True,
                task_id=cmd.task_id,
                affected_tasks=affected_tasks
            )

        except Exception as e:
            return ReviewTaskResult(
                success=False,
                task_id=cmd.task_id,
                affected_tasks=[],
                error=str(e)
            )
