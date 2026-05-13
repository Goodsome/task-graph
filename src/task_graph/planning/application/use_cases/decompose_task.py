import logging
from dataclasses import dataclass
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.application.dtos.decompose_task_command import (
    DecomposeTaskCommand,
)
from task_graph.planning.application.dtos.decompose_task_result import (
    DecomposeTaskResult,
)
from typing import Self


logger = logging.getLogger(__name__)


@dataclass
class DecomposeTask:
    """Decompose a task into sub-tasks.

    This use case:
    1. Retrieves the task by ID.
    2. Generates sub-tasks based on the task's output.
    3. Persists the new sub-tasks.
    4. Marks the original task as DELEGATED.
    5. Persists the original task."""

    uow: UnitOfWork[TaskRepository]

    def execute(self: Self, cmd: DecomposeTaskCommand) -> DecomposeTaskResult:
        with self.uow:
            task_id = TaskId.reconstitute(cmd.task_id)
            task = self.uow.repository.get(task_id)
            sub_tasks = task.generate_sub_tasks()
            for sub_task in sub_tasks:
                self.uow.repository.add(sub_task)
            task.mark_delegated()
            self.uow.repository.save(task)
            self.uow.commit()
            return DecomposeTaskResult(
                success=True,
                task_id=str(task.id),
                sub_task_ids=[str(st.id) for st in sub_tasks],
            )