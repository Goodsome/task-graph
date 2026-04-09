from __future__ import annotations
from typing import Any
from pydantic import Field, model_serializer, model_validator
from task_graph.shared.domain.core.value_object import ValueObject


class IssueDescription(ValueObject):
    """Description of an issue, max 10000 characters"""

    value: str = Field(
        ...,
        max_length=10000,
        description="Issue description must not exceed 10000 characters",
    )

    @classmethod
    def create(cls, value: str) -> IssueDescription:
        """Create a new IssueDescription instance"""
        return cls(value=value.strip())

    @model_serializer
    def serialize(self) -> str:
        return self.value

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"value": data}
        return data
