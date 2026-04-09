import logging
from typing import Union
from dataclasses import dataclass, field
from task_graph.planning.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.value_objects import TaskId

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class DeleteTaskCommand:
    task_id: str


@dataclass(frozen=True)
class DeleteTaskResult:
    success: bool
    error: str | None = field(default="")


@dataclass
class DeleteTask:
    uow: UnitOfWork

    def execute(self, cmd: DeleteTaskCommand) -> DeleteTaskResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                self.uow.tasks.delete(task_id)
                self.uow.commit() # Wait, delete might not have events, but needs commit.
                return DeleteTaskResult(success=True)
        except Exception as e:
            logger.error(f"Failed to delete task {cmd.task_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return DeleteTaskResult(success=False, error=str(e))
