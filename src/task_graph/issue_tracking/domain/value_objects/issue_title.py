from __future__ import annotations
from typing import Any
from pydantic import Field, model_serializer, model_validator
from task_graph.shared.domain.core.value_object import ValueObject


class IssueTitle(ValueObject):
    """Title of an issue, max 200 characters"""

    value: str = Field(
        ...,
        max_length=200,
        min_length=1,
        description="Issue title must be between 1 and 200 characters",
    )

    @classmethod
    def create(cls, value: str) -> IssueTitle:
        """Create a new IssueTitle instance"""
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Issue title cannot be empty")
        return cls(value=cleaned_value)

    @model_serializer
    def serialize(self) -> str:
        return self.value

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"value": data}
        return data
