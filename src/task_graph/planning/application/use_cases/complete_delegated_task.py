from dataclasses import dataclass, field

from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.aggregates.task import Task
from task_graph.planning.domain.enums import TaskStatus
from task_graph.planning.domain.exceptions import TaskNotFoundError
from task_graph.planning.domain.value_objects.task_id import TaskId


@dataclass(frozen=True)
class CompleteDelegatedTaskCommand:
    task_id: str


@dataclass(frozen=True)
class CompleteDelegatedTaskResult:
    status: str
    task_id: str
    message: str


@dataclass
class CompleteDelegatedTask:
    uow: UnitOfWork[TaskRepository]

    def execute(self, cmd: CompleteDelegatedTaskCommand) -> CompleteDelegatedTaskResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.repository.get(task_id)

                if task.status != TaskStatus.DELEGATED:
                    return CompleteDelegatedTaskResult(
                        status="skipped",
                        task_id=cmd.task_id,
                        message=f"Task status is {task.status.value}, expected delegated",
                    )

                sub_tasks = self.uow.repository.find_by_parent_id(task_id)
                if sub_tasks:
                    unfinished = [t for t in sub_tasks if t.status != TaskStatus.DONE]
                    if unfinished:
                        unfinished_ids = ", ".join(str(t.id) for t in unfinished)
                        return CompleteDelegatedTaskResult(
                            status="skipped",
                            task_id=cmd.task_id,
                            message=f"Subtasks not done: {unfinished_ids}",
                        )

                task.mark_decomposition_completed()
                self.uow.repository.save(task)
                self.uow.commit()

                return CompleteDelegatedTaskResult(
                    status="success",
                    task_id=cmd.task_id,
                    message="Decomposition completed",
                )

        except Exception as e:
            return CompleteDelegatedTaskResult(
                status="failed",
                task_id=cmd.task_id,
                message=str(e),
            )
