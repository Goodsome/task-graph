from event_hub import DomainEvent
from pydantic import Field
from task_graph.issue_tracking.domain.enums import IssueType, Severity


class IssueCreatedEvent(DomainEvent):
    """Event emitted when a new issue is reported."""
    issue_id: str = Field(description="Issue ID")
    project_id: str = Field(description="Project ID the issue belongs to")
    title: str = Field(description="Issue title")
    type: IssueType = Field(description="Issue type")
    severity: Severity = Field(description="Issue severity")
    submitter_name: str = Field(description="Name of the person who submitted the issue")
