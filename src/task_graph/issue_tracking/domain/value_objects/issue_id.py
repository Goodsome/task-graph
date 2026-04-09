from __future__ import annotations
from typing import Any
from uuid import UUID, uuid4
from pydantic import model_serializer, model_validator
from task_graph.shared.domain.core.value_object import ValueObject


class IssueId(ValueObject):
    """Unique identifier for an Issue"""

    value: UUID

    @classmethod
    def create(cls) -> IssueId:
        """Create a new IssueId with a random UUID"""
        return cls(value=uuid4())

    @classmethod
    def reconstitute(cls, value: UUID | str) -> IssueId:
        """Reconstruct an IssueId from a UUID or string"""
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
