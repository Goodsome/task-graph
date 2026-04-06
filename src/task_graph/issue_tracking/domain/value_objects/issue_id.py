from __future__ import annotations

from uuid import UUID
from task_graph.shared.models import ValueObject


class IssueId(ValueObject):
    """Unique identifier for an Issue"""

    value: UUID

    def create(self) -> IssueId: ...

    def reconstitute(self, value: UUID) -> IssueId: ...

    def __str__(self) -> str: ...

    def serialize(self) -> str: ...
