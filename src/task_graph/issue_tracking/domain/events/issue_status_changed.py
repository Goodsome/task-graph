from event_hub import DomainEvent
from pydantic import Field
from task_graph.issue_tracking.domain.enums import IssueStatus


class IssueStatusChangedEvent(DomainEvent):
    """Event emitted when an issue's status is changed."""
    issue_id: str = Field(description="Issue ID")
    old_status: IssueStatus = Field(description="Old status")
    new_status: IssueStatus = Field(description="New status")
    changed_by: str = Field(description="Name of the person who changed the status")
