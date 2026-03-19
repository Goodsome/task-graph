from task_graph.issue_tracking.domain.ports.issue_event_publisher import (
    IssueEventPublisher,
)
from pydantic import BaseModel, Field
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository


class UnlinkIssueFromTaskCommand(BaseModel):
    issue_id: str
    task_id: str


class UnlinkIssueFromTaskResult(BaseModel):
    success: bool
    error: str = Field(default="")


@dataclass
class UnlinkIssueFromTask:
    """Unlink an issue from a task"""

    issue_repository: IssueRepository
    event_publisher: IssueEventPublisher

    def execute(self, cmd: UnlinkIssueFromTaskCommand) -> UnlinkIssueFromTaskResult: ...
