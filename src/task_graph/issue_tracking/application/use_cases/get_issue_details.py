from pydantic import BaseModel, Field
from typing import Union
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository


class GetIssueDetailsQuery(BaseModel):
    issue_id: str


class GetIssueDetailsResult(BaseModel):
    success: bool
    issue: dict | None = Field(default=None)
    error: str | None = Field(default=None)


@dataclass
class GetIssueDetails:
    """Get full issue details including comments and labels"""

    issue_repository: IssueRepository

    def execute(self, query: GetIssueDetailsQuery) -> GetIssueDetailsResult: ...
