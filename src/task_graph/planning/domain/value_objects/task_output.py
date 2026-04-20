from pydantic import Field
from task_graph.shared.domain.core.value_object import ValueObject
from task_graph.planning.domain.value_objects.sub_task_info import SubTaskInfo


class TaskOutput(ValueObject):
    """任务执行者的交付物"""

    summary: str
    artifacts: list[str]
    error: str | None = Field(default=None)
    sub_tasks: list[SubTaskInfo] | None = Field(default=None, description="要拆分的子任务列表")
