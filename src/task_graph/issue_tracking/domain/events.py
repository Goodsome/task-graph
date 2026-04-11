from task_graph.shared.domain.core.domain_event import DomainEvent
from pydantic import Field
from task_graph.issue_tracking.domain.enums import IssueStatus, IssueType, Severity


class IssueCreatedEvent(DomainEvent):
    """Event emitted when a new issue is reported."""
    issue_id: str = Field(description="Issue ID")
    project_id: str = Field(description="Project ID the issue belongs to")
    title: str = Field(description="Issue title")
    type: IssueType = Field(description="Issue type")
    severity: Severity = Field(description="Issue severity")
    submitter_name: str = Field(description="Name of the person who submitted the issue")


class IssueStatusChangedEvent(DomainEvent):
    """Event emitted when an issue's status is changed."""
    issue_id: str = Field(description="Issue ID")
    old_status: IssueStatus = Field(description="Old status")
    new_status: IssueStatus = Field(description="New status")
    changed_by: str = Field(description="Name of the person who changed the status")


class IssueClosedEvent(DomainEvent):
    """Event emitted when an issue is closed."""
    issue_id: str = Field(description="Issue ID")
    resolution: str | None = Field(description="Optional resolution note")


class IssueCommentAddedEvent(DomainEvent):
    """Event emitted when a new comment is added to an issue."""
    issue_id: str = Field(description="Issue ID")
    comment_id: str = Field(description="Comment ID")
    author: str = Field(description="Comment author")
    content: str = Field(description="Comment content")
