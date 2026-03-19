from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from pydantic import BaseModel, Field
from task_graph.issue_tracking.domain.enums import IssueType, Severity
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository


class CreateIssueCommand(BaseModel):
    title: str
    description: str
    type: IssueType
    severity: Severity
    submitter_name: str
    submitter_email: str


class CreateIssueResult(BaseModel):
    success: bool
    issue_id: str
    error: str = Field(default="")


@dataclass
class CreateIssue:
    """Create a new issue with initial status NEW"""

    issue_repository: IssueRepository
    event_publisher: IssueEventPublisher

    def execute(self, cmd: CreateIssueCommand) -> CreateIssueResult: ...
