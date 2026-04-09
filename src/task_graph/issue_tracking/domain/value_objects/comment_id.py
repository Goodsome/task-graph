from typing import Self, Any
from uuid import UUID, uuid4
from pydantic import model_serializer, model_validator
from task_graph.shared.domain.core.value_object import ValueObject


class CommentId(ValueObject):
    """Unique identifier for a Comment"""

    value: UUID

    @classmethod
    def create(cls) -> Self:
        return cls(value=uuid4())

    @classmethod
    def reconstitute(cls, value: UUID | str) -> Self:
        if isinstance(value, str):
            value = UUID(value)
        return cls(value=value)

    def __str__(self) -> str:
        return str(self.value)

    @model_serializer
    def serialize(self) -> str:
        return str(self.value)

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, (str, UUID)):
            return {"value": data}
        return data
