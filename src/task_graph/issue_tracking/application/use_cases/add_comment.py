from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from pydantic import BaseModel, Field
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository


class AddCommentCommand(BaseModel):
    issue_id: str
    content: str
    author: str


class AddCommentResult(BaseModel):
    success: bool
    comment_id: str
    error: str = Field(default="")


@dataclass
class AddComment:
    """Add a comment to an issue"""

    issue_repository: IssueRepository
    event_publisher: IssueEventPublisher

    def execute(self, cmd: AddCommentCommand) -> AddCommentResult: ...
