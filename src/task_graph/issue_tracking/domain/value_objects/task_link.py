from __future__ import annotations
from datetime import datetime, timezone
from pydantic import model_validator
from task_graph.shared.domain.core.value_object import ValueObject
from task_graph.planning.domain.value_objects.task_id import TaskId


class TaskLink(ValueObject):
    """Link between an Issue and a Task from Planning context"""

    task_id: TaskId
    linked_at: datetime

    @classmethod
    def create(cls, task_id: TaskId | str) -> TaskLink:
        """Create a new TaskLink instance"""
        if isinstance(task_id, str):
            task_id = TaskId.reconstitute(task_id)
        return cls(
            task_id=task_id,
            linked_at=datetime.now(timezone.utc)
        )

    @model_validator(mode="before")
    @classmethod
    def validate_from_orm(cls, data: dict | object) -> dict:
        """Support converting ORM models to TaskLink"""
        if isinstance(data, dict):
            return data
        # 处理ORM对象
        return {
            "task_id": getattr(data, "task_id", None),
            "linked_at": getattr(data, "linked_at", None),
        }
