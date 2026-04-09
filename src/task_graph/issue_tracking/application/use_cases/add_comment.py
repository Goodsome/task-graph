from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from pydantic import BaseModel, Field
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId


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

    def execute(self, cmd: AddCommentCommand) -> AddCommentResult:
        try:
            # Parse issue ID
            issue_id = IssueId.reconstitute(cmd.issue_id)

            # Find issue
            issue = self.issue_repository.find_by_id(issue_id)
            if not issue:
                return AddCommentResult(
                    success=False,
                    comment_id="",
                    error=f"Issue {cmd.issue_id} not found"
                )

            # Add comment
            comment = issue.add_comment(
                content=cmd.content,
                author=cmd.author
            )

            # Persist changes
            self.issue_repository.save(issue)

            # Publish event
            # TODO: Publish CommentAdded event

            return AddCommentResult(
                success=True,
                comment_id=str(comment.id)
            )
        except Exception as e:
            return AddCommentResult(
                success=False,
                comment_id="",
                error=str(e)
            )

