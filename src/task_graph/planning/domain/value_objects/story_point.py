from typing import Any

from pydantic import Field, model_validator, model_serializer, field_validator

from task_graph.shared.models import ValueObject


class StoryPoint(ValueObject):
    """Encapsulated Fibonacci number representing effort (1, 2, 3, 5, 8, 13...)."""

    value: int = Field(..., gt=0, description="Effort points must be positive")

    @classmethod
    def create(cls, effort: int) -> 'StoryPoint':
        return cls(value=effort)

    @model_serializer
    def serialize(self) -> int:
        return self.value

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, int):
            return {"value": data}
        return data

    @field_validator('value')
    @classmethod
    def validate_fibonacci(cls, v: int) -> int:
        valid_points = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89} # 敏捷开发常用范围
        if v not in valid_points:
            raise ValueError(f"Value must be a valid Fibonacci story point: {valid_points}")
        return v

    # 支持数学运算重载，方便 PriorityAnalysisService 计算
    def __add__(self, other):
        if isinstance(other, StoryPoint):
            return StoryPoint.create(self.value + other.value)
        if isinstance(other, int):
            return StoryPoint.create(self.value + other)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __lt__(self, other):
        if isinstance(other, StoryPoint):
            return self.value < other.value
        return self.value < other