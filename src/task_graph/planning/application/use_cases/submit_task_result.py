from task_graph.planning.application.ports.unit_of_work import UnitOfWork
from task_graph.planning.domain.value_objects.task_id import TaskId
from task_graph.planning.domain.value_objects.task_output import TaskOutput
from task_graph.planning.domain.value_objects.sub_task_info import SubTaskInfo
from dataclasses import dataclass, field
from typing import Union, Optional

from pydantic import BaseModel, Field


class SubmitTaskResultCommand(BaseModel):
    """Command to submit task execution result."""
    task_id: str
    summary: str
    artifacts: list[str] = Field(default_factory=list)
    error: Optional[str] = None
    sub_tasks: list[SubTaskInfo] = Field(default_factory=list)


@dataclass(frozen=True)
class SubmitTaskResultResult:

    success: bool
    error: str | None = field(default=None)


@dataclass
class SubmitTaskResult:
    """Submit task execution result with artifacts and optional error. Updates task.output."""

    uow: UnitOfWork

    def execute(self, cmd: SubmitTaskResultCommand) -> SubmitTaskResultResult:
        try:
            with self.uow:
                # 1. 查找任务
                task_id = TaskId.reconstitute(cmd.task_id)
                task = self.uow.tasks.get(task_id)
                
                if not task:
                    return SubmitTaskResultResult(
                        success=False,
                        error=f"Task {cmd.task_id} not found"
                    )
                
                # 2. 创建 TaskOutput
                task_output = TaskOutput(
                    summary=cmd.summary,
                    artifacts=cmd.artifacts if cmd.artifacts else [],
                    error=cmd.error,
                    sub_tasks=cmd.sub_tasks
                )
                
                # 3. 设置任务输出
                task.set_output(task_output)
                
                # 4. 保存任务
                self.uow.tasks.save(task)
                
                for event in task.collect_events():
                    self.uow.event_bus.publish(event)
                
                self.uow.commit()
                
                return SubmitTaskResultResult(success=True)
                
        except Exception as e:
            return SubmitTaskResultResult(
                success=False,
                error=str(e)
            )

