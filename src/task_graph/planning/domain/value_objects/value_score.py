from typing import Any

from pydantic import Field, model_serializer, model_validator

from task_graph.shared.models import ValueObject


class ValueScore(ValueObject):
    """Numeric representation of business value."""

    value: float = Field(..., gt=0)

    @classmethod
    def create(cls, value: float) -> 'ValueScore':
        return cls(value=value)

    def __add__(self, other):
        if isinstance(other, ValueScore):
            return ValueScore.create(self.value + other.value)
        if isinstance(other, (int, float)):
            return ValueScore.create(self.value + other)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    @model_serializer
    def serialize(self) -> float:
        return self.value

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, int):
            return {"value": data}
        return data

