from pydantic import BaseModel, Field
from task_graph.issue_tracking.domain.enums import IssueType, Severity


class UpdateIssueMetadataCommand(BaseModel):
    issue_id: str
    type: IssueType | None = Field(default=None)
    severity: Severity | None = Field(default=None)
    add_labels: list[str] | None = Field(default=None)
    remove_labels: list[str] | None = Field(default=None)
