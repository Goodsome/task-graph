from typing import Self
from uuid import UUID
from datetime import datetime, timezone
from pydantic import model_validator
from task_graph.issue_tracking.domain.value_objects.comment_id import CommentId
from task_graph.shared.domain.core.entity import Entity


class Comment(Entity):
    """Comment attached to an Issue, immutable after creation"""

    id: CommentId
    content: str
    author: str
    created_at: datetime

    @classmethod
    def create(cls, content: str, author: str) -> Self:
        """Create a new Comment instance"""
        if not content.strip():
            raise ValueError("Comment content cannot be empty")
        if not author.strip():
            raise ValueError("Comment author cannot be empty")

        return cls(
            id=CommentId.create(),
            content=content.strip(),
            author=author.strip(),
            created_at=datetime.now(timezone.utc)
        )

    @model_validator(mode="before")
    @classmethod
    def validate_primitive_types(cls, data: dict | object) -> dict:
        """Convert primitive types to proper value objects when reconstructing"""
        # 支持ORM对象
        if not isinstance(data, dict):
            # 转换ORM对象为字典
            data = {
                "id": getattr(data, "id", None),
                "content": getattr(data, "content", None),
                "author": getattr(data, "author", None),
                "created_at": getattr(data, "created_at", None),
            }

        if isinstance(data.get("id"), (str, UUID)):
            data["id"] = CommentId.reconstitute(data["id"])
        return data
