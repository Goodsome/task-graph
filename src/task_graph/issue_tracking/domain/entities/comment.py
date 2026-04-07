from typing import Self
from datetime import datetime
from task_graph.issue_tracking.domain.value_objects.comment_id import CommentId
from task_graph.shared.domain.core.entity import Entity


class Comment(Entity):
    """Comment attached to an Issue, immutable after creation"""

    id: CommentId
    content: str
    author: str
    created_at: datetime

    @classmethod
    def create(cls, content: str, author: str) -> Self: ...
