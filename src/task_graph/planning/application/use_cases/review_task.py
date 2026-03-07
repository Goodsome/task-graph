from dataclasses import dataclass, field
from task_graph.planning.domain.services.dependency_resolution_service import (
    DependencyResolutionService,
)
from task_graph.planning.application.unit_of_work import UnitOfWork
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

    uow: UnitOfWork
    resolution_service: DependencyResolutionService

    def execute(self, cmd: ReviewTaskCommand) -> ReviewTaskResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.tasks.get(task_id)

                if not task:
                    return ReviewTaskResult(
                        success=False,
                        task_id=cmd.task_id,
                        affected_tasks=[],
                        error=f"Task {cmd.task_id} not found"
                    )

                task.review(approved=cmd.approved, feedback=cmd.feedback)
                self.uow.tasks.save(task)

                affected_tasks = []
                modified_dependents = []
                if task.is_done():
                    dependents = self.uow.tasks.find_dependents(task.id)
                    for dependent in dependents:
                        if dependent.status in [TaskStatus.BLOCKED, TaskStatus.PENDING]:
                            is_blocked = self.resolution_service.evaluate_blocking_status(dependent, self.uow.tasks)
                            
                            if not is_blocked:
                                dependent._update_status(TaskStatus.READY)
                                self.uow.tasks.save(dependent)
                                affected_tasks.append(str(dependent.id.value))
                                modified_dependents.append(dependent)
                                
                for event in task.collect_events():
                    self.uow.event_bus.publish(event)
                for dep in modified_dependents:
                    for event in dep.collect_events():
                        self.uow.event_bus.publish(event)

                self.uow.commit()

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
