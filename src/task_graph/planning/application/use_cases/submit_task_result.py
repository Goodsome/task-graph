from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from dataclasses import dataclass
from typing import Self
from task_graph.planning.application.dtos.submit_task_result_command import (
    SubmitTaskResultCommand,
)
from task_graph.planning.application.dtos.submit_task_result_result import (
    SubmitTaskResultResult,
)


@dataclass
class SubmitTaskResult:
    """Submit task execution result with artifacts and optional error. Updates task.output."""

    uow: UnitOfWork[TaskRepository]

    def execute(self: Self, cmd: SubmitTaskResultCommand) -> SubmitTaskResultResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.repository.get(task_id)
                task_output = TaskOutput(
                    summary=cmd.summary,
                    artifacts=cmd.artifacts if cmd.artifacts else [],
                    error=cmd.error,
                    sub_tasks=cmd.sub_tasks,
                )
                task.set_output(task_output)
                self.uow.repository.save(task)
                self.uow.commit()
                return SubmitTaskResultResult(success=True)
        except Exception as e:
            return SubmitTaskResultResult(success=False, error=str(e))
