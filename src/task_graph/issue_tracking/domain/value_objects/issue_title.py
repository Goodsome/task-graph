from __future__ import annotations

from pydantic import Field
from task_graph.shared.domain.core.value_object import ValueObject


class IssueTitle(ValueObject):
    """Title of an issue, max 200 characters"""

    value: str = Field(
        default=Field(
            ...,
            max_length=200,
            description="Issue title must not exceed 200 characters",
        )
    )

    @classmethod
    def create(cls, value: str) -> IssueTitle: ...

    def serialize(self) -> str: ...
