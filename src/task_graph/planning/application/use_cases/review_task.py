from dataclasses import dataclass, field
from task_graph.planning.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.value_objects.task_id import TaskId


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

    def execute(self, cmd: ReviewTaskCommand) -> ReviewTaskResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.tasks.get(task_id)

                task.review(approved=cmd.approved, feedback=cmd.feedback)
                self.uow.tasks.save(task)
                self.uow.commit()
                                
                return ReviewTaskResult(
                    success=True,
                    task_id=cmd.task_id,
                )

        except Exception as e:
            return ReviewTaskResult(
                success=False,
                task_id=cmd.task_id,
                affected_tasks=[],
                error=str(e)
            )
