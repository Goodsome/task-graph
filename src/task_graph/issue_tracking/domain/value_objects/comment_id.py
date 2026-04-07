from __future__ import annotations

from uuid import UUID
from task_graph.shared.domain.core.value_object import ValueObject


class CommentId(ValueObject):
    """Unique identifier for a Comment"""

    value: UUID

    def create(self) -> CommentId: ...

    def reconstitute(self, value: Union[UUID, str]) -> CommentId: ...

    def __str__(self) -> str: ...

    def serialize(self) -> str: ...
