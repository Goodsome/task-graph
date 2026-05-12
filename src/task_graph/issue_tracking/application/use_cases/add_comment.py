from dataclasses import dataclass
import logging
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.application.dtos.add_comment_command import (
    AddCommentCommand,
)
from typing import Self
from task_graph.issue_tracking.application.dtos.add_comment_result import (
    AddCommentResult,
)

logger = logging.getLogger(__name__)


@dataclass
class AddComment:
    """Add a comment to an issue"""

    uow: UnitOfWork[IssueRepository]

    def execute(self: Self, cmd: AddCommentCommand) -> AddCommentResult:
        try:
            with self.uow:
                issue_id = IssueId.reconstitute(cmd.issue_id)
                issue = self.uow.repository.find_by_id(issue_id)
                if not issue:
                    return AddCommentResult(
                        success=False,
                        comment_id="",
                        error=f"Issue {cmd.issue_id} not found",
                    )
                comment = issue.add_comment(content=cmd.content, author=cmd.author)
                self.uow.repository.save(issue)
                logger.info(f"Comment added to issue {issue.id} by {cmd.author}")
                self.uow.commit()
                return AddCommentResult(success=True, comment_id=str(comment.id))
        except Exception as e:
            return AddCommentResult(success=False, comment_id="", error=str(e))
