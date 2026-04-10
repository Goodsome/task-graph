from __future__ import annotations
from pydantic import Field, model_validator
from task_graph.shared.domain.core.value_object import ValueObject
from typing import Self, Any


class Submitter(ValueObject):
    """Information about the issue submitter"""

    name: str = Field(..., min_length=1, max_length=100)

    @classmethod
    def create(cls, name: str) -> Self:
        """Create a new Submitter instance"""
        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValueError("Submitter name cannot be empty")
        return cls(name=cleaned_name)

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"name": data}
        if not isinstance(data, dict) and hasattr(data, "name"):
            return {"name": data.name}
        return data
