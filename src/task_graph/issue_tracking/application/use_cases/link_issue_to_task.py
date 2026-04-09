from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from pydantic import BaseModel, Field
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId


class LinkIssueToTaskCommand(BaseModel):
    issue_id: str
    task_id: str


class LinkIssueToTaskResult(BaseModel):
    success: bool
    error: str = Field(default="")


@dataclass
class LinkIssueToTask:
    """Link an issue to a task from Planning context"""

    issue_repository: IssueRepository
    event_publisher: IssueEventPublisher

    def execute(self, cmd: LinkIssueToTaskCommand) -> LinkIssueToTaskResult:
        try:
            # Parse issue ID
            issue_id = IssueId.reconstitute(cmd.issue_id)

            # Find issue
            issue = self.issue_repository.find_by_id(issue_id)
            if not issue:
                return LinkIssueToTaskResult(
                    success=False,
                    error=f"Issue {cmd.issue_id} not found"
                )

            # Link to task
            issue.link_to_task(task_id=cmd.task_id)

            # Persist changes
            self.issue_repository.save(issue)

            # Publish event
            # TODO: Publish IssueLinkedToTask event

            return LinkIssueToTaskResult(success=True)
        except Exception as e:
            return LinkIssueToTaskResult(
                success=False,
                error=str(e)
            )

