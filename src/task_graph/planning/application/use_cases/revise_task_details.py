from task_graph.planning.application.ports.unit_of_work import UnitOfWork
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

    uow: UnitOfWork

    def execute(self, cmd: ReviseTaskDetailsCommand) -> ReviseTaskDetailsResult:
        try:
            with self.uow:
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.tasks.get(task_id)

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

                self.uow.tasks.save(task)
                self.uow.commit()
                return ReviseTaskDetailsResult(True)

        except Exception as e:
            return ReviseTaskDetailsResult(False, str(e))
