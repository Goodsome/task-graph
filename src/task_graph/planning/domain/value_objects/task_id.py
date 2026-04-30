from typing import Any, override

from pydantic import model_serializer, model_validator

from task_graph.shared.domain.core.value_object import ValueObject
from uuid import UUID, uuid4


class TaskId(ValueObject):
    """Unique identifier for a Task."""

    value: UUID

    @classmethod
    def create(cls):
        return cls(value=uuid4())
    
    @classmethod
    def reconstitute(cls, value: UUID | str):
        if isinstance(value, str):
            value = UUID(value)
        return cls(value=value)
    
    @override
    def __str__(self):
        return str(self.value)

    @override
    def __hash__(self) -> int:
        return hash(self.value)

    @model_serializer
    def serialize(self) -> str:
        return str(self.value)

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, (str, UUID)):
            return {"value": data}
        return data
    