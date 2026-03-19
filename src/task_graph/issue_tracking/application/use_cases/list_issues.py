from pydantic import BaseModel, Field
from typing import Union
from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType
from dataclasses import dataclass
from task_graph.issue_tracking.domain.ports.issue_repository import IssueRepository


class ListIssuesQuery(BaseModel):
    status: IssueStatus | None = Field(default=None)
    type: IssueType | None = Field(default=None)
    labels: list[str] | None = Field(default=None)
    limit: int = Field(default=10)
    offset: int = Field(default=0)


class ListIssuesResult(BaseModel):
    issues: list[dict]
    total_count: int
    error: str | None = Field(default=None)


@dataclass
class ListIssues:
    """Paginated list of issues with filtering"""

    issue_repository: IssueRepository

    def execute(self, query: ListIssuesQuery) -> ListIssuesResult: ...
