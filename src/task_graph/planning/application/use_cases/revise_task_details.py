from task_graph.planning.domain.ports.task_repository import TaskRepository
from typing import Union
from dataclasses import dataclass, field

from task_graph.planning.domain.value_objects import TaskId, StoryPoint, ValueScore


from pydantic import BaseModel

class ReviseTaskDetailsCommand(BaseModel):

    task_id: str
    name: str | None = None
    description: str | None = None
    effort: int | None = None
    base_value: float | None = None


@dataclass(frozen=True)
class ReviseTaskDetailsResult:

    success: bool
    error: str = ""


@dataclass
class ReviseTaskDetails:
    """Revise a task's details like name, description, effort, or base value."""

    repository: TaskRepository

    def execute(self, cmd: ReviseTaskDetailsCommand) -> ReviseTaskDetailsResult:
        try:
            task_id = TaskId.reconstitute(cmd.task_id)
            task = self.repository.get(task_id)
            if not task:
                return ReviseTaskDetailsResult(False, f"Task {cmd.task_id} not found")

            # 增量更新
            if cmd.name is not None:
                task.name = cmd.name

            if cmd.description is not None:
                task.description = cmd.description

            if cmd.effort is not None:
                # 触发 Pydantic 校验
                task.effort = StoryPoint.create(cmd.effort)

            if cmd.base_value is not None:
                task.base_value = ValueScore.create(cmd.base_value)

            self.repository.save(task)
            return ReviseTaskDetailsResult(True)

        except Exception as e:
            return ReviseTaskDetailsResult(False, str(e))
