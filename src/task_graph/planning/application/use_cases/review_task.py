from dataclasses import dataclass, field
from task_graph.planning.application.ports.unit_of_work import UnitOfWork
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

    def execute(self, cmd: ReviewTaskCommand) -> ReviewTaskResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.tasks.get(task_id)

                task.review(approved=cmd.approved, feedback=cmd.feedback)
                self.uow.tasks.save(task)

                affected_tasks = []
                sub_tasks = []
                
                if task.status == TaskStatus.DECOMPOSING:
                    sub_tasks = task.generate_sub_tasks()
                    for sub in sub_tasks:
                        self.uow.tasks.save(sub)
                        affected_tasks.append(str(sub.id.value))

                self.uow.commit()
                                
                for sub_task in sub_tasks:
                    for event in sub_task.collect_events():
                        self.uow.event_bus.publish(event)


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
