from event_hub import DomainEvent
from pydantic import Field


class IssueCommentAdded(DomainEvent):
    """Event emitted when a new comment is added to an issue."""
    issue_id: str = Field(description="Issue ID")
    comment_id: str = Field(description="Comment ID")
    author: str = Field(description="Comment author")
    content: str = Field(description="Comment content")
