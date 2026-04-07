from __future__ import annotations

from pydantic import Field
from task_graph.shared.domain.core.value_object import ValueObject


class Label(ValueObject):
    """Label for categorizing issues"""

    name: str = Field(
        default=Field(
            ..., max_length=50, description="Label name must not exceed 50 characters"
        )
    )
    color: str | None = Field(default=None)

    def create(self, name: str, color: str | None = None) -> Label: ...
