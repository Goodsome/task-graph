from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from pydantic import BaseModel, Field
from typing import Union
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository


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

    def execute(self, cmd: CloseIssueCommand) -> CloseIssueResult: ...
