from __future__ import annotations
from typing import Any
from pydantic import Field, model_validator
from task_graph.shared.domain.core.value_object import ValueObject


class Label(ValueObject):
    """Label for categorizing issues"""

    name: str = Field(
        ...,
        max_length=50,
        min_length=1,
        description="Label name must be between 1 and 50 characters"
    )
    color: str | None = Field(default=None, pattern=r'^#[0-9a-fA-F]{6}$')

    @classmethod
    def create(cls, name: str, color: str | None = None) -> Label:
        """Create a new Label instance"""
        cleaned_name = name.strip().lower()
        if not cleaned_name:
            raise ValueError("Label name cannot be empty")
        return cls(name=cleaned_name, color=color)

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"name": data}
        return data
