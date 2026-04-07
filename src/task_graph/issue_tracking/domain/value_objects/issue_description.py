from __future__ import annotations

from pydantic import Field
from task_graph.shared.domain.core.value_object import ValueObject


class IssueDescription(ValueObject):
    """Description of an issue, max 10000 characters"""

    value: str = Field(
        default=Field(
            ...,
            max_length=10000,
            description="Issue description must not exceed 10000 characters",
        )
    )

    @classmethod
    def create(cls, value: str) -> IssueDescription: ...

    def serialize(self) -> str: ...
