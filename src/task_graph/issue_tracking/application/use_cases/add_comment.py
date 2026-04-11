from pydantic import BaseModel, Field
from dataclasses import dataclass
import logging
from task_graph.issue_tracking.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId

logger = logging.getLogger(__name__)


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

    uow: UnitOfWork

    def execute(self, cmd: AddCommentCommand) -> AddCommentResult:
        try:
            with self.uow:
                # Parse issue ID
                issue_id = IssueId.reconstitute(cmd.issue_id)

                # Find issue
                issue = self.uow.issues.find_by_id(issue_id)
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
                self.uow.issues.save(issue)
                logger.info(f"Comment added to issue {issue.id} by {cmd.author}")

                # Collect and publish all domain events
                events = issue.collect_events()
                logger.debug(f"Collected {len(events)} events from issue aggregate")
                for event in events:
                    self.uow.event_bus.publish(event)

                # Commit transaction
                self.uow.commit()

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

