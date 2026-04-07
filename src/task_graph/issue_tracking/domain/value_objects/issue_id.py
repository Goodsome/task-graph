from __future__ import annotations

from uuid import UUID
from task_graph.shared.domain.core.value_object import ValueObject


class IssueId(ValueObject):
    """Unique identifier for an Issue"""

    value: UUID

    @classmethod
    def create(cls) -> IssueId: ...

    @classmethod
    def reconstitute(cls, value: UUID) -> IssueId: ...

    def __str__(self) -> str: ...

    def serialize(self) -> str: ...
