from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from pydantic import BaseModel, Field
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId
from task_graph.issue_tracking.domain.enums import IssueStatus


class CloseIssueCommand(BaseModel):
    issue_id: str
    resolution: str | None = Field(default=None)


class CloseIssueResult(BaseModel):
    success: bool
    error: str = Field(default="")


@dataclass
class CloseIssue:
    """Close an issue that is in RESOLVED status"""

    issue_repository: IssueRepository
    event_publisher: IssueEventPublisher

    def execute(self, cmd: CloseIssueCommand) -> CloseIssueResult:
        try:
            # Parse issue ID
            issue_id = IssueId.reconstitute(cmd.issue_id)

            # Find issue
            issue = self.issue_repository.find_by_id(issue_id)
            if not issue:
                return CloseIssueResult(
                    success=False,
                    error=f"Issue {cmd.issue_id} not found"
                )

            # Close issue
            issue.close(resolution=cmd.resolution)

            # Persist changes
            self.issue_repository.save(issue)

            # Publish event
            # TODO: Publish IssueClosed event

            return CloseIssueResult(success=True)
        except Exception as e:
            return CloseIssueResult(
                success=False,
                error=str(e)
            )

