from dataclasses import dataclass
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.application.dtos.review_task_command import ReviewTaskCommand
from task_graph.planning.application.dtos.review_task_result import ReviewTaskResult
from typing import Self


@dataclass
class ReviewTask:
    uow: UnitOfWork[TaskRepository]

    def execute(self: Self, cmd: ReviewTaskCommand) -> ReviewTaskResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.repository.get(task_id)
                task.review(approved=cmd.approved, feedback=cmd.feedback)
                self.uow.repository.save(task)
                self.uow.commit()
                return ReviewTaskResult(success=True, task_id=cmd.task_id)
        except Exception as e:
            return ReviewTaskResult(
                success=False, task_id=cmd.task_id, affected_tasks=[], error=str(e)
            )
