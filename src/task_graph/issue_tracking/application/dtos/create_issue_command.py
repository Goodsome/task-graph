from task_graph.issue_tracking.domain.enums import IssueType, Severity
from pydantic import BaseModel


class CreateIssueCommand(BaseModel):
    project_id: str
    title: str
    description: str
    type: IssueType
    severity: Severity
    submitter_name: str
