from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from pydantic import BaseModel, Field
from task_graph.issue_tracking.domain.enums import IssueType, Severity
from typing import Union
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository


class UpdateIssueMetadataCommand(BaseModel):
    issue_id: str
    type: IssueType | None = Field(default=None)
    severity: Severity | None = Field(default=None)
    add_labels: list[str] | None = Field(default=None)
    remove_labels: list[str] | None = Field(default=None)


class UpdateIssueMetadataResult(BaseModel):
    success: bool
    error: str = Field(default="")


@dataclass
class UpdateIssueMetadata:
    """Update issue metadata like type, severity, and labels"""

    issue_repository: IssueRepository
    event_publisher: IssueEventPublisher

    def execute(self, cmd: UpdateIssueMetadataCommand) -> UpdateIssueMetadataResult: ...
