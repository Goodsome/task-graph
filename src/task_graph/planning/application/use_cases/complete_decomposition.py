from dataclasses import dataclass, field

from task_graph.planning.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.domain.value_objects.task_id import TaskId


@dataclass(frozen=True)
class CompleteDecompositionCommand:
    task_id: str


@dataclass(frozen=True)
class CompleteDecompositionResult:
    status: str
    task_id: str
    message: str


@dataclass
class CompleteDecomposition:
    uow: UnitOfWork

    def execute(self, cmd: CompleteDecompositionCommand) -> CompleteDecompositionResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.tasks.get(task_id)

                if not task:
                    return CompleteDecompositionResult(
                        status="failed",
                        task_id=cmd.task_id,
                        message=f"Task {cmd.task_id} not found",
                    )

                if task.status != TaskStatus.DECOMPOSING:
                    return CompleteDecompositionResult(
                        status="skipped",
                        task_id=cmd.task_id,
                        message=f"Task status is {task.status.value}, expected decomposing",
                    )

                sub_tasks = self.uow.tasks.find_by_parent_id(task_id)
                if sub_tasks:
                    unfinished = [t for t in sub_tasks if t.status != TaskStatus.DONE]
                    if unfinished:
                        unfinished_ids = ", ".join(str(t.id) for t in unfinished)
                        return CompleteDecompositionResult(
                            status="skipped",
                            task_id=cmd.task_id,
                            message=f"Subtasks not done: {unfinished_ids}",
                        )

                task.mark_decomposition_completed()
                self.uow.tasks.save(task)

                for event in task.collect_events():
                    self.uow.event_bus.publish(event)

                self.uow.commit()

                return CompleteDecompositionResult(
                    status="success",
                    task_id=cmd.task_id,
                    message="Decomposition completed",
                )

        except Exception as e:
            return CompleteDecompositionResult(
                status="failed",
                task_id=cmd.task_id,
                message=str(e),
            )
