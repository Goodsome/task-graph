import logging
from typing import Union
from dataclasses import dataclass, field
from task_graph.planning.domain.ports.task_repository import TaskRepository
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
    repository: TaskRepository

    def execute(self, cmd: DeleteTaskCommand) -> DeleteTaskResult:
        try:
            task_id = TaskId.reconstitute(cmd.task_id)
            self.repository.delete(task_id)
            return DeleteTaskResult(success=True)
        except Exception as e:
            logger.error(f"Failed to delete task {cmd.task_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return DeleteTaskResult(success=False, error=str(e))
