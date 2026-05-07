
from pydantic import BaseModel, Field
from dataclasses import dataclass
import logging
from task_graph.shared.application.ports.unit_of_work import UnitOfWork
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId

logger = logging.getLogger(__name__)
class CloseIssueCommand(BaseModel):
    issue_id: str
    resolution: str | None = Field(default=None)
class CloseIssueResult(BaseModel):
    success: bool
    error: str = Field(default="")
@dataclass
class CloseIssue:
    """Close an issue that is in RESOLVED status"""

    uow: UnitOfWork[IssueRepository]

    def execute(self, cmd: CloseIssueCommand) -> CloseIssueResult:
        try:
            with self.uow:
                # Parse issue ID
                issue_id = IssueId.reconstitute(cmd.issue_id)

                # Find issue
                issue = self.uow.repository.find_by_id(issue_id)
                if not issue:
                    return CloseIssueResult(
                        success=False,
                        error=f"Issue {cmd.issue_id} not found"
                    )

                # Close issue
                issue.close(resolution=cmd.resolution)

                # Persist changes
                self.uow.repository.save(issue)
                logger.info(f"Issue {issue.id} closed")
                # Commit transaction
                self.uow.commit()

                return CloseIssueResult(success=True)
        except Exception as e:
            return CloseIssueResult(
                success=False,
                error=str(e)
            )
