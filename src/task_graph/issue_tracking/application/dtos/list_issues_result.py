from pydantic import BaseModel, Field
from task_graph.issue_tracking.application.dtos.issue_summary_dto import IssueSummaryDTO


class ListIssuesResult(BaseModel):
    issues: list[IssueSummaryDTO]
    total_count: int
    error: str = Field(default="")
