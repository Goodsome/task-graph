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

    def execute(self, cmd: UpdateIssueStatusCommand) -> UpdateIssueStatusResult: ...
