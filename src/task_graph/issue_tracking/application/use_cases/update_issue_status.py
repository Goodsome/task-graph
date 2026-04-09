from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from pydantic import BaseModel, Field
from dataclasses import dataclass
from task_graph.issue_tracking.domain.enums import IssueStatus
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.services.issue_status_transition_service import (
    IssueStatusTransitionService,
)
from task_graph.issue_tracking.domain.value_objects.issue_id import IssueId


class UpdateIssueStatusCommand(BaseModel):
    issue_id: str
    new_status: IssueStatus
    changed_by: str


class UpdateIssueStatusResult(BaseModel):
    success: bool
    error: str = Field(default="")


@dataclass
class UpdateIssueStatus:
    """Update issue status with state machine validation"""

    issue_repository: IssueRepository
    event_publisher: IssueEventPublisher
    status_transition_service: IssueStatusTransitionService

    def execute(self, cmd: UpdateIssueStatusCommand) -> UpdateIssueStatusResult:
        try:
            # Parse issue ID
            issue_id = IssueId.reconstitute(cmd.issue_id)

            # Find issue
            issue = self.issue_repository.find_by_id(issue_id)
            if not issue:
                return UpdateIssueStatusResult(
                    success=False,
                    error=f"Issue {cmd.issue_id} not found"
                )

            # Validate transition
            self.status_transition_service.validate_transition(
                current_status=issue.status,
                target_status=cmd.new_status
            )

            # Update status
            issue.change_status(
                new_status=cmd.new_status,
                changed_by=cmd.changed_by
            )

            # Persist changes
            self.issue_repository.save(issue)

            # Publish event
            # TODO: Publish IssueStatusChanged event

            return UpdateIssueStatusResult(success=True)
        except Exception as e:
            return UpdateIssueStatusResult(
                success=False,
                error=str(e)
            )

