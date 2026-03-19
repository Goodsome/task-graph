from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from pydantic import BaseModel, Field
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository


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

    def execute(self, cmd: LinkIssueToTaskCommand) -> LinkIssueToTaskResult: ...
