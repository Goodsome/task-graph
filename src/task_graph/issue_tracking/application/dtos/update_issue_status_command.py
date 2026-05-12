from task_graph.issue_tracking.domain.enums import IssueStatus
from pydantic import BaseModel


class UpdateIssueStatusCommand(BaseModel):
    issue_id: str
    new_status: IssueStatus
    changed_by: str
