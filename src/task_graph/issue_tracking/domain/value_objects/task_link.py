from __future__ import annotations

from task_graph.shared.models import ValueObject
from datetime import datetime


class TaskLink(ValueObject):
    """Link between an Issue and a Task from Planning context"""

    task_id: str
    linked_at: datetime

    def create(self, task_id: str) -> TaskLink: ...
