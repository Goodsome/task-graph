import logging
from typing import Self
from dataclasses import dataclass
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.ports.task_repository import TaskRepository
from task_graph.planning.domain.value_objects import TaskId
from task_graph.planning.application.dtos.delete_task_result import DeleteTaskResult
from task_graph.planning.application.dtos.delete_task_command import DeleteTaskCommand

logger = logging.getLogger(__name__)


@dataclass
class DeleteTask:
    uow: UnitOfWork[TaskRepository]

    def execute(self: Self, cmd: DeleteTaskCommand) -> DeleteTaskResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                self.uow.repository.delete(task_id)
                self.uow.commit()
                return DeleteTaskResult(success=True)
        except Exception as e:
            logger.error(f"Failed to delete task {cmd.task_id}: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return DeleteTaskResult(success=False, error=str(e))
