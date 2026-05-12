from pydantic import BaseModel, Field
from task_graph.issue_tracking.application.dtos.issue_details_dto import IssueDetailsDTO


class GetIssueDetailsResult(BaseModel):
    success: bool
    issue: IssueDetailsDTO | None = Field(default=None)
    error: str = Field(default="")
