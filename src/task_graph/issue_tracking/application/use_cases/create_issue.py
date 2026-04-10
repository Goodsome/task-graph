from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from pydantic import BaseModel, Field
from task_graph.issue_tracking.domain.enums import IssueType, Severity
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository
from task_graph.issue_tracking.domain.aggregates.issue import Issue
from task_graph.issue_tracking.domain.value_objects.submitter import Submitter


class CreateIssueCommand(BaseModel):
    title: str
    description: str
    type: IssueType
    severity: Severity
    submitter_name: str


class CreateIssueResult(BaseModel):
    success: bool
    issue_id: str
    error: str = Field(default="")


@dataclass
class CreateIssue:
    """Create a new issue with initial status NEW"""

    issue_repository: IssueRepository
    event_publisher: IssueEventPublisher

    def execute(self, cmd: CreateIssueCommand) -> CreateIssueResult:
        try:
            # Create submitter value object
            submitter = Submitter.create(
                name=cmd.submitter_name,
            )

            # Create issue aggregate
            issue = Issue.create(
                title=cmd.title,
                description=cmd.description,
                issue_type=cmd.type,
                severity=cmd.severity,
                submitter=submitter,
            )

            # Persist issue
            self.issue_repository.save(issue)

            # Publish domain event
            # TODO: Create IssueCreated event and publish

            return CreateIssueResult(success=True, issue_id=str(issue.id))
        except Exception as e:
            return CreateIssueResult(success=False, issue_id="", error=str(e))
