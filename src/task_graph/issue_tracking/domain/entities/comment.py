from __future__ import annotations

from datetime import datetime
from task_graph.issue_tracking.domain.value_objects.comment_id import CommentId
from task_graph.shared.models import Entity


class Comment(Entity):
    """Comment attached to an Issue, immutable after creation"""

    id: CommentId
    content: str
    author: str
    created_at: datetime

    def create(self, content: str, author: str) -> Comment: ...
