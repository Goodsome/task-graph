from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from typing import Self
from dataclasses import dataclass
from task_graph.planning.domain.value_objects import StoryPoint, TaskId, ValueScore
from task_graph.planning.application.dtos.revise_task_details_command import (
    ReviseTaskDetailsCommand,
)
from task_graph.planning.application.dtos.revise_task_details_result import (
    ReviseTaskDetailsResult,
)


@dataclass
class ReviseTaskDetails:
    """Revise a task's details like name, description, effort, or base value."""

    uow: UnitOfWork[TaskRepository]

    def execute(self: Self, cmd: ReviseTaskDetailsCommand) -> ReviseTaskDetailsResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.repository.get(task_id)
                if cmd.name is not None:
                    task.name = cmd.name
                if cmd.description is not None:
                    task.description = cmd.description
                if cmd.effort is not None:
                    task.effort = StoryPoint.create(cmd.effort)
                if cmd.base_value is not None:
                    task.base_value = ValueScore.create(cmd.base_value)
                self.uow.repository.save(task)
                self.uow.commit()
                return ReviseTaskDetailsResult(success=True)
        except Exception as e:
            return ReviseTaskDetailsResult(success=False, error=str(e))
