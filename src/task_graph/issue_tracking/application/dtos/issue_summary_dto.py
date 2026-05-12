from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity
from pydantic import BaseModel
from datetime import datetime


class IssueSummaryDTO(BaseModel):
    id: str
    project_id: str
    title: str
    type: IssueType
    severity: Severity
    status: IssueStatus
    submitter_name: str
    comment_count: int
    label_count: int
    task_link_count: int
    created_at: datetime
    updated_at: datetime
