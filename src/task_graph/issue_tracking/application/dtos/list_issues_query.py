from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from pydantic import BaseModel, Field


class ListIssuesQuery(BaseModel):
    status: IssueStatus | None = Field(default=None)
    type: IssueType | None = Field(default=None)
    severity: Severity | None = Field(default=None)
    labels: list[str] | None = Field(default=None)
    project_id: str | None = Field(default=None)
    limit: int = Field(default=10)
    offset: int = Field(default=0)
