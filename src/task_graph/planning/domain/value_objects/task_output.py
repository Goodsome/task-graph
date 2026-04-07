from typing import Union
from pydantic import Field
from task_graph.shared.domain.core.value_object import ValueObject


class TaskOutput(ValueObject):
    """任务执行者的交付物"""

    summary: str
    artifacts: list[str]
    error: str | None = Field(default=None)
