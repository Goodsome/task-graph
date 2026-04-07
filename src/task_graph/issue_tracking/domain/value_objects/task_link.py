from __future__ import annotations

from task_graph.shared.domain.core.value_object import ValueObject
from datetime import datetime


class TaskLink(ValueObject):
    """Link between an Issue and a Task from Planning context"""

    task_id: str
    linked_at: datetime

    @classmethod
    def create(cls, task_id: str) -> TaskLink: ...
